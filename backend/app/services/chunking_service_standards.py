"""
智能分块服务
根据不同的法律结构采用不同的分块策略
确保每个向量块大小适中、语义完整
"""

from typing import Dict, List, Tuple
import re


class ChunkingService:
    """智能分块服务：将法律文档分块以便向量化"""
    
    def __init__(self):
        self.min_chunk_size = 200      # 最小分块大小（字符）
        self.max_chunk_size = 1000     # 最大分块大小（字符）
        self.target_chunk_size = 500   # 目标分块大小（字符）
        self.articles_per_chunk = 3    # 每个分块的目标条数
    
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
        策略1：有章节结构的法律
        原则：
        1. 同章节的条可以组合
        2. 不同章节的条��能混合
        3. 每个块3-5条，或单条>800字独立成块
        4. 孤儿条款<200字向前合并
        
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
        
        chunks = []
        current_group = []
        current_size = 0
        
        for i, article in enumerate(articles):
            article_content = article['content']
            article_size = len(article_content)
            
            # 判断：单条过长（>800字）独立成块
            if article_size > 800:
                # 先保存当前组
                if current_group:
                    chunks.append(self._create_chunk(
                        current_group, chapter_num, chapter_title,
                        section_num, section_title, references,
                        start_index + len(chunks)
                    ))
                    current_group = []
                    current_size = 0
                
                # 单条独立成块
                chunks.append(self._create_chunk(
                    [article], chapter_num, chapter_title,
                    section_num, section_title, references,
                    start_index + len(chunks)
                ))
                continue
            
            # 判断：加入当前组是否超过最大值
            if current_size + article_size > self.max_chunk_size and current_group:
                # 当前组已满，保存并开新组
                chunks.append(self._create_chunk(
                    current_group, chapter_num, chapter_title,
                    section_num, section_title, references,
                    start_index + len(chunks)
                ))
                current_group = [article]
                current_size = article_size
            else:
                # 加入当前组
                current_group.append(article)
                current_size += article_size
            
            # 判断：当前组已达到目标条数且大小合适
            if (len(current_group) >= self.articles_per_chunk and 
                current_size >= self.target_chunk_size):
                chunks.append(self._create_chunk(
                    current_group, chapter_num, chapter_title,
                    section_num, section_title, references,
                    start_index + len(chunks)
                ))
                current_group = []
                current_size = 0
        
        # 处理最后一组（可能是孤儿条款）
        if current_group:
            # 如果最后一组太小且前面有块，尝试合并到前一块
            if current_size < self.min_chunk_size and chunks:
                last_chunk = chunks[-1]
                last_chunk_size = len(last_chunk['chunk_text'])
                
                # 合并后不超过最大值
                if last_chunk_size + current_size <= self.max_chunk_size:
                    # 合并到前一块
                    merged_articles = self._get_articles_from_chunk(last_chunk, articles)
                    merged_articles.extend(current_group)
                    
                    chunks[-1] = self._create_chunk(
                        merged_articles, chapter_num, chapter_title,
                        section_num, section_title, references,
                        start_index + len(chunks) - 1
                    )
                else:
                    # 无法合并，独立成块
                    chunks.append(self._create_chunk(
                        current_group, chapter_num, chapter_title,
                        section_num, section_title, references,
                        start_index + len(chunks)
                    ))
            else:
                # 独立成块
                chunks.append(self._create_chunk(
                    current_group, chapter_num, chapter_title,
                    section_num, section_title, references,
                    start_index + len(chunks)
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
        策略2：无章节结构的法律（只有条）
        按语义相关性分组，每3-5条一组
        
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

