"""
智能分块服务（法律文档版）
根据不同的法律结构采用不同的分块策略
当前法律条文统一采用：一条法条 = 一个 chunk

══════════════════════════════════════════════════════════════
  📌 拆分规则速查（想改规则？直接跳到对应行）
══════════════════════════════════════════════════════════════

  ① 策略选择入口（如何判断用哪种策略）
     → chunk_document()          第 20 行
       - 有章节 + 有条文          → 策略1  chunk_with_chapters()
       - 无章节 + 有条文          → 策略2  chunk_without_chapters()
       - 无结构（通知/公告）      → 策略3  chunk_unstructured()

  ② 策略1（有章节结构的法律）
     → chunk_with_chapters()     第 95 行
     核心规则：逐条循环，每条单独调用 _create_chunk([article], ...)
     即：一条法条 = 一个向量块，章节信息作为元数据保留

  ③ 策略2（无章节结构的法律）
     → chunk_without_chapters()  第 284 行
     核心规则：同策略1，逐条生成块

  ④ 策略3（无结构文档：通知、公告）
     → chunk_unstructured()      第 296 行
     核心规则：按段落（\\n\\n 分隔）合并，超过 max_chunk_size(1000字) 就切分

  ⑤ 块的内容组装（每个块里放什么字段）
     → _create_chunk()           第 188 行
       - chunk_text：正文（含条号 + 条文内容 + 引用全文）
       - keywords：从正文提取的关键词列表
       - chapter_number / article_start 等元数据

  ⑥ 尺寸参数（控制块的大小）
     → __init__()                第 14 行
       - min_chunk_size  = 200   最小字符数
       - max_chunk_size  = 1000  最大字符数（策略3 用）
       - target_chunk_size = 500 目标字符数（当前策略1/2 未使用）

══════════════════════════════════════════════════════════════
  📂 文件位置：backend/app/services/chunking_service.py
  📂 准则版本：backend/app/services/chunking_service_standards.py
  📂 被哪里调用：backend/app/services/document_processor.py
══════════════════════════════════════════════════════════════
"""

from typing import Dict, List
import re


class ChunkingService:
    """分块服务：法律条文统一一条一块，附件与无结构文档按原逻辑处理"""

    def __init__(self):
        self.min_chunk_size = 200
        self.max_chunk_size = 1000
        self.target_chunk_size = 500
        self.articles_per_chunk = 1

    def chunk_document(self, text: str, structure: Dict) -> List[Dict]:
        """
        主入口：根据文档结构选择分块策略

        Args:
            text: 文档全文
            structure: 结构信息（来自 structure_parser）

        Returns:
            分块列表
        """
        articles = structure.get('articles', [])
        chapters = structure.get('chapters', [])
        sections = structure.get('sections', [])
        references = structure.get('references', {})

        print(f"\n📦 开始智能分块...")
        print(f"   文档统计：{len(chapters)} 章, {len(sections)} 节, {len(articles)} 条")

        if len(chapters) > 0 and len(articles) > 0:
            print(f"   📋 采用策略1：有章节结构，一条一块")
            chunks = self.chunk_with_chapters(articles, chapters, sections, references)
        elif len(articles) > 0:
            print(f"   📋 采用策略2：无章节结构，一条一块")
            chunks = self.chunk_without_chapters(articles, references)
        else:
            print(f"   📋 采用策略3：无结构文档分块")
            chunks = self.chunk_unstructured(text)

        print(f"   ✅ 分块完成：生成 {len(chunks)} 个向量块")

        self._validate_chunks(chunks)

        attachments = structure.get('attachments', [])
        if attachments:
            print(f"   📎 处理附件：{len(attachments)} 个")
            for attachment in attachments:
                att_type = attachment.get('type', '附件')

                if 'natural_text' in attachment and attachment['natural_text']:
                    att_text = attachment['natural_text']
                    print(f"      ✅ 使用 AI 自然语言: {att_type}")
                else:
                    line_num = attachment.get('line_num', 0)
                    text_lines = text.split('\n')
                    att_parts = []
                    if line_num > 0 and line_num <= len(text_lines):
                        for j in range(line_num - 1, len(text_lines)):
                            att_parts.append(text_lines[j].strip())

                    att_text = '\n'.join(att_parts)
                    print(f"      ⚠️  使用原始文本: {att_type}")

                if att_text and len(att_text) > 10:
                    chunks.append({
                        'chunk_index': len(chunks),
                        'chunk_text': att_text,
                        'expanded_text': None,
                        'chunk_type': 'attachment',
                        'chapter_number': None,
                        'chapter_title': None,
                        'section_number': None,
                        'section_title': None,
                        'article_start': att_type,
                        'article_end': None,
                        'articles_included': [],
                        'articles_count': 0,
                        'has_references': False,
                        'reference_articles': [],
                        'keywords': self._extract_keywords(att_text)
                    })
                    print(f"      ✅ 附件块 {len(chunks)-1}: {att_type}")

        return chunks

    def chunk_with_chapters(
        self,
        articles: List[Dict],
        chapters: List[Dict],
        sections: List[Dict],
        references: Dict
    ) -> List[Dict]:
        """
        策略1：有章节结构的法律
        当前统一规则：一条法条 = 一个 chunk
        """
        chunks = []
        chunk_index = 0

        for chapter in chapters:
            chapter_num = chapter['number']
            chapter_sections = [s for s in sections if s.get('chapter') == chapter_num]

            if chapter_sections:
                for section in chapter_sections:
                    section_num = section['number']
                    section_articles = [
                        a for a in articles
                        if a.get('chapter') == chapter_num and a.get('section') == section_num
                    ]

                    for article in section_articles:
                        chunks.append(self._create_chunk(
                            [article],
                            chapter_num,
                            chapter.get('title', ''),
                            section_num,
                            section.get('title', ''),
                            references,
                            chunk_index
                        ))
                        chunk_index += 1
            else:
                chapter_articles = [
                    a for a in articles
                    if a.get('chapter') == chapter_num
                ]

                for article in chapter_articles:
                    chunks.append(self._create_chunk(
                        [article],
                        chapter_num,
                        chapter.get('title', ''),
                        None,
                        None,
                        references,
                        chunk_index
                    ))
                    chunk_index += 1

        orphan_articles = [a for a in articles if not a.get('chapter')]
        for article in orphan_articles:
            chunks.append(self._create_chunk(
                [article], None, None, None, None, references, chunk_index
            ))
            chunk_index += 1

        return chunks

    def _chunk_articles_group(
        self,
        articles: List[Dict],
        chapter_num: str,
        chapter_title: str,
        section_num: str,
        section_title: str,
        references: Dict,
        start_index: int
    ) -> List[Dict]:
        """
        兼容旧调用：当前也统一一条一块
        """
        if not articles:
            return []

        chunks = []
        for idx, article in enumerate(articles):
            chunks.append(self._create_chunk(
                [article],
                chapter_num,
                chapter_title,
                section_num,
                section_title,
                references,
                start_index + idx
            ))
        return chunks

    def _create_chunk(
        self,
        articles: List[Dict],
        chapter_num: str,
        chapter_title: str,
        section_num: str,
        section_title: str,
        references: Dict,
        chunk_index: int
    ) -> Dict:
        """
        创建一个分块
        """
        article_numbers = [a['number'] for a in articles]
        article_contents = [a['content'] for a in articles]

        chunk_text = '\n\n'.join(article_contents)
        expanded_text = self._expand_references(chunk_text, references, articles)
        keywords = []

        return {
            'chunk_index': chunk_index,
            'chunk_text': chunk_text,
            'expanded_text': expanded_text if expanded_text != chunk_text else None,
            'chunk_type': 'single_article',
            'chapter_number': chapter_num,
            'chapter_title': chapter_title,
            'section_number': section_num,
            'section_title': section_title,
            'article_start': article_numbers[0] if article_numbers else None,
            'article_end': article_numbers[-1] if article_numbers else None,
            'articles_included': article_numbers,
            'articles_count': 1 if article_numbers else 0,
            'has_references': bool(references and any(a in references for a in article_numbers)),
            'reference_articles': self._get_reference_articles(article_numbers, references),
            'keywords': keywords
        }

    def _expand_references(
        self,
        chunk_text: str,
        references: Dict,
        all_articles: List[Dict]
    ) -> str:
        """
        展开引用："依照第X条" → 插入第X条的内容
        """
        expanded = chunk_text

        for article_num, refs in references.items():
            if article_num in chunk_text:
                for ref_article in refs:
                    ref_content = None
                    for article in all_articles:
                        if article['number'] == ref_article:
                            ref_content = article['content']
                            break

                    if ref_content:
                        if '【引用展开】' not in expanded:
                            expanded += '\n\n【引用展开】\n'
                        expanded += f'\n{ref_article}：{ref_content}\n'

        return expanded

    def _get_reference_articles(self, article_numbers: List[str], references: Dict) -> List[str]:
        """获取本块中条文引用的其他条文"""
        ref_articles = []
        for article_num in article_numbers:
            if article_num in references:
                ref_articles.extend(references[article_num])
        return list(set(ref_articles))

    def _get_articles_from_chunk(self, chunk: Dict, all_articles: List[Dict]) -> List[Dict]:
        """从分块中提取原始条文对象"""
        article_numbers = chunk['articles_included']
        return [a for a in all_articles if a['number'] in article_numbers]

    def _extract_keywords(self, text: str) -> List[str]:
        """
        提取关键词（简单版本：正则匹配常见法律术语）
        """
        keyword_patterns = [
            r'劳动合同', r'用人单位', r'劳动者', r'工资', r'社会保险',
            r'解除', r'终止', r'赔偿', r'补偿', r'违约', r'试用期',
            r'经济补偿金', r'违约金', r'竞业限制', r'保密协议',
            r'工作时间', r'休息休假', r'加班', r'年假'
        ]

        keywords = []
        for pattern in keyword_patterns:
            if re.search(pattern, text):
                keywords.append(pattern.replace('\\', ''))

        return list(set(keywords))[:10]

    def chunk_without_chapters(self, articles: List[Dict], references: Dict) -> List[Dict]:
        """
        策略2：无章节结构的法律
        当前统一规则：一条法条 = 一个 chunk
        """
        chunks = []
        for idx, article in enumerate(articles):
            chunks.append(self._create_chunk(
                [article], None, None, None, None, references, idx
            ))
        return chunks

    def chunk_unstructured(self, text: str) -> List[Dict]:
        """
        策略3：无结构文档（通知、公告）
        按段落或固定大小分块
        """
        chunks = []

        if len(text) <= self.max_chunk_size:
            chunks.append({
                'chunk_index': 0,
                'chunk_text': text,
                'chunk_type': 'full_document',
                'chapter_number': None,
                'section_number': None,
                'article_start': None,
                'article_end': None,
                'articles_included': [],
                'keywords': self._extract_keywords(text)
            })
        else:
            paragraphs = text.split('\n\n')
            current_chunk = []
            current_size = 0
            chunk_index = 0

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                para_size = len(para)

                if current_size + para_size > self.max_chunk_size and current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunks.append({
                        'chunk_index': chunk_index,
                        'chunk_text': chunk_text,
                        'chunk_type': 'paragraph_group',
                        'chapter_number': None,
                        'section_number': None,
                        'article_start': f'段落{chunk_index*10+1}-{chunk_index*10+len(current_chunk)}',
                        'article_end': None,
                        'articles_included': [],
                        'keywords': self._extract_keywords(chunk_text)
                    })

                    current_chunk = [para]
                    current_size = para_size
                    chunk_index += 1
                else:
                    current_chunk.append(para)
                    current_size += para_size

            if current_chunk:
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append({
                    'chunk_index': chunk_index,
                    'chunk_text': chunk_text,
                    'chunk_type': 'paragraph_group',
                    'chapter_number': None,
                    'section_number': None,
                    'article_start': f'段落{chunk_index*10+1}-{chunk_index*10+len(current_chunk)}',
                    'article_end': None,
                    'articles_included': [],
                    'keywords': self._extract_keywords(chunk_text)
                })

        return chunks

    def _validate_chunks(self, chunks: List[Dict]):
        """验证分块质量"""
        if not chunks:
            print("   ⚠️  警告：没有生成分块")
            return

        sizes = [len(c['chunk_text']) for c in chunks]
        avg_size = sum(sizes) / len(sizes)

        too_small = sum(1 for s in sizes if s < self.min_chunk_size)
        too_large = sum(1 for s in sizes if s > self.max_chunk_size)

        print(f"\n   📊 分块质量检查：")
        print(f"      总块数: {len(chunks)}")
        print(f"      平均大小: {avg_size:.0f} 字符")
        print(f"      过小(<{self.min_chunk_size}): {too_small} 个")
        print(f"      过大(>{self.max_chunk_size}): {too_large} 个")

        if too_small > len(chunks) * 0.2:
            print(f"      ⚠️  警告：过小的块较多，属于一条一块后的正常现象，可后续再做专项校验")
        if too_large > 0:
            print(f"      ⚠️  警告：有过大的块，可能影响检索精度")


chunking_service = ChunkingService()
