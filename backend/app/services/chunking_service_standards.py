"""
智能分块服务（行业准则版）
根据不同的文档结构采用不同的分块策略
当前准则文档统一采用：一条条款 = 一个 chunk

══════════════════════════════════════════════════════════════
  📌 拆分规则速查（想改规则？直接跳到对应行）
══════════════════════════════════════════════════════════════

  ① 策略选择入口（如何判断用哪种策略）
     → chunk_document()            第 20 行
       - 有章节 + 有条文            → 策略1  chunk_with_chapters()
       - 无章节 + 有条文            → 策略2  chunk_without_chapters()
       - 无结构（通知/公告）        → 策略3  chunk_unstructured()

  ② 策略1（有章节结构的准则）
     → chunk_with_chapters()       第 104 行
     → _chunk_articles_group()     第 186 行  ← 核心拆分逻辑在这里
     核心规则（第 214 行注释）：
       一条条款 = 一个向量块，绝不与其他条合并
       即：for article in articles → _create_chunk([article], ...)

  ③ 策略2（无章节结构的准则）
     → chunk_without_chapters()    第 359 行
     核心规则：同策略1，委托给 _chunk_articles_group()

  ④ 策略3（无结构文档：通知、公告）
     → chunk_unstructured()        第 375 行
     核心规则：按段落（\\n\\n 分隔）合并，超过 max_chunk_size(1000字) 就切分

  ⑤ 块的内容组装（每个块里放什么字段）
     → _create_chunk()             第 228 行
       - chunk_text：正文（含条号 + 条文内容 + 引用全文）
       - keywords：从正文提取的关键词列表
       - chapter_number / article_start 等元数据

  ⑥ 尺寸参数（控制块的大小）
     → __init__()                  第 14 行
       - min_chunk_size  = 200     最小字符数
       - max_chunk_size  = 1000    最大字符数（策略3 用）
       - target_chunk_size = 500   目标字符数（当前策略1/2 未使用）
       - articles_per_chunk = 3    保留参数，当前未使用

══════════════════════════════════════════════════════════════
  📂 文件位置：backend/app/services/chunking_service_standards.py
  📂 法律版本：backend/app/services/chunking_service.py
  📂 被哪里调用：backend/app/services/document_processor_standards.py
══════════════════════════════════════════════════════════════
"""

from typing import Dict, List, Tuple
import re


class ChunkingService:
    """分块服务（行业准则版）：准则条款统一一条一块，附件与无结构文档按原逻辑处理"""
    
    def __init__(self):
        self.min_chunk_size = 200      # 最小分块大小（字符）
        self.max_chunk_size = 1000     # 最大分块大小（字符）
        self.target_chunk_size = 500   # 目标分块大小（字符）
        self.articles_per_chunk = 3    # 每个分块的目标条数（保留供参考，当前未使用）
    
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
        
        # 选择分块策略
        if len(chapters) > 0 and len(articles) > 0:
            # 策略1：有章节结构
            print(f"   📋 采用策略1：有章节结构分块")
            chunks = self.chunk_with_chapters(articles, chapters, sections, references)
        elif len(articles) > 0:
            # 策略2：无章节，只有条
            print(f"   📋 采用策略2：无章节结构分块")
            chunks = self.chunk_without_chapters(articles, references)
        else:
            # 策略3：无结构（通知、公告）
            print(f"   📋 采用策略3：无结构文档分块")
            chunks = self.chunk_unstructured(text)
        
        print(f"   ✅ 分块完成：生成 {len(chunks)} 个向量块")
        
        # 验证分块质量
        self._validate_chunks(chunks)
        
        
        # 处理附件（在返回前添加）
        attachments = structure.get('attachments', [])
        if attachments:
            print(f"   📎 处理附件：{len(attachments)} 个")
            for attachment in attachments:
                att_type = attachment.get('type', '附件')
                
                # 🆕 优先使用 AI 转换后的自然语言
                if 'natural_text' in attachment and attachment['natural_text']:
                    att_text = attachment['natural_text']
                    print(f"      ✅ 使用 AI 自然语言: {att_type}")
                else:
                    # 备用：从原文提取附件内容
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
        策略1：有章节结构的准则文档
        规则：一条条款 = 一个向量块，按章节归属保留元数据
        
        Args:
            articles: 条文列表
            chapters: 章列表
            sections: 节列表
            references: 引用关系
            
        Returns:
            分块列表
        """
        chunks = []
        chunk_index = 0
        
        # 按章节组织条文
        for chapter in chapters:
            chapter_num = chapter['number']
            
            # 获取本章的所有节
            chapter_sections = [s for s in sections if s.get('chapter') == chapter_num]
            
            if chapter_sections:
                # 有节，按节分组
                for section in chapter_sections:
                    section_num = section['number']
                    section_articles = [
                        a for a in articles 
                        if a.get('chapter') == chapter_num and a.get('section') == section_num
                    ]
                    
                    # 对本节的条进行分块
                    section_chunks = self._chunk_articles_group(
                        section_articles, 
                        chapter_num, 
                        chapter.get('title', ''),
                        section_num,
                        section.get('title', ''),
                        references,
                        chunk_index
                    )
                    
                    chunks.extend(section_chunks)
                    chunk_index += len(section_chunks)
            else:
                # 无节，按章分组
                chapter_articles = [
                    a for a in articles 
                    if a.get('chapter') == chapter_num
                ]
                
                chapter_chunks = self._chunk_articles_group(
                    chapter_articles,
                    chapter_num,
                    chapter.get('title', ''),
                    None,
                    None,
                    references,
                    chunk_index
                )
                
                chunks.extend(chapter_chunks)
                chunk_index += len(chapter_chunks)
        
        # 处理没有章节的条（如果有）
        orphan_articles = [a for a in articles if not a.get('chapter')]
        if orphan_articles:
            orphan_chunks = self._chunk_articles_group(
                orphan_articles, None, None, None, None, references, chunk_index
            )
            chunks.extend(orphan_chunks)
        
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
        对一组条文进行分块（同章节或同节）
        
        Args:
            articles: 条文列表
            chapter_num: 章号
            chapter_title: 章标题
            section_num: 节号
            section_title: 节标题
            references: 引用关系
            start_index: 起始索引
            
        Returns:
            分块列表
        """
        if not articles:
            return []
        
        # standards 专用规则：一条法条 = 一个向量块，绝不与其他条合并
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
        
        Args:
            articles: 条文列表
            chapter_num: 章号
            chapter_title: 章标题
            section_num: 节号
            section_title: 节标题
            references: 引用关系
            chunk_index: 分块索引
            
        Returns:
            分块字典
        """
        article_numbers = [a['number'] for a in articles]
        article_contents = [a['content'] for a in articles]
        
        # 合并内容
        chunk_text = '\n\n'.join(article_contents)
        
        # 检查是否有引用需要展开
        expanded_text = self._expand_references(chunk_text, references, articles)
        
        # 提取关键词（简单版本）
        keywords = self._extract_keywords(chunk_text)
        
        return {
            'chunk_index': chunk_index,
            'chunk_text': chunk_text,
            'expanded_text': expanded_text if expanded_text != chunk_text else None,
            'chunk_type': 'single_article' if len(articles) == 1 else 'article_group',
            'chapter_number': chapter_num,
            'chapter_title': chapter_title,
            'section_number': section_num,
            'section_title': section_title,
            'article_start': article_numbers[0] if article_numbers else None,
            'article_end': article_numbers[-1] if article_numbers else None,
            'articles_included': article_numbers,
            'articles_count': len(articles),
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
        
        Args:
            chunk_text: 分块文本
            references: 引用关系
            all_articles: 所有条文
            
        Returns:
            展开后的文本
        """
        expanded = chunk_text
        
        # 查找本块中提到的引用
        for article_num, refs in references.items():
            if article_num in chunk_text:
                # 本块包含有引用的条
                for ref_article in refs:
                    # 查找被引用的条文内容
                    ref_content = None
                    for article in all_articles:
                        if article['number'] == ref_article:
                            ref_content = article['content']
                            break
                    
                    if ref_content:
                        # 在文本末尾添加引用展开
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
        
        Args:
            text: 文本
            
        Returns:
            关键词列表
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
        
        return list(set(keywords))[:10]  # 最多10个关键词
    
    def chunk_without_chapters(self, articles: List[Dict], references: Dict) -> List[Dict]:
        """
        策略2：无章节结构的准则文档（只有条）
        规则：一条条款 = 一个向量块
        
        Args:
            articles: 条文列表
            references: 引用关系
            
        Returns:
            分块列表
        """
        return self._chunk_articles_group(
            articles, None, None, None, None, references, 0
        )
    
    def chunk_unstructured(self, text: str) -> List[Dict]:
        """
        策略3：无结构文档（通知、公告）
        按段落或固定大小分块
        
        Args:
            text: 文档全文
            
        Returns:
            分块列表
        """
        chunks = []
        
        # 如果文档很短，整篇作为一块
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
            # 按段落分块
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
                    # 保存当前块
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
            
            # 最后一块
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
            print(f"      ⚠️  警告：过小的块较多，可能需要调整策略")
        if too_large > 0:
            print(f"      ⚠️  警告：有过大的块，可能影响检索精度")


# 创建全局实例
chunking_service = ChunkingService()


# 测试代码
if __name__ == '__main__':
    print("智能分块服务已加载")
    print(f"配置：最小={chunking_service.min_chunk_size}, "
          f"目标={chunking_service.target_chunk_size}, "
          f"最大={chunking_service.max_chunk_size}")

