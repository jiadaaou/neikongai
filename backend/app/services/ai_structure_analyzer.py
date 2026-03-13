"""
AI 结构分析服务
使用通义千问识别文档中的附加内容（附件、附表、附注、注释等）
并将其转换为自然语言描述
"""

from dashscope import Generation
import dashscope
import json
import os
import re
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class AIStructureAnalyzer:
    """使用通义千问分析法律文档结构"""
    
    def __init__(self):
        # 设置 API Key
        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if not dashscope.api_key:
            raise ValueError("未设置 DASHSCOPE_API_KEY 环境变量")
        
        # 使用 qwen-max 模型（理解能力最强）
        self.model = 'qwen-max'
        
        print(f"✅ AI 结构分析服务初始化成功")
        print(f"   模型: {self.model}")
    
    def identify_attachments(self, full_text: str) -> list:
        """
        用 AI 识别文档中的所有附加内容
        
        Args:
            full_text: 文档全文
            
        Returns:
            [
                {
                    'type': '附：车船税税目税额表',
                    'start_marker': '附：',
                    'line_num': 47,
                    'content_type': '表格',
                    'description': '车船税各类车辆的税率表'
                }
            ]
        """
        print(f"\n🤖 使用 AI 识别附加内容...")
        print(f"   文档长度: {len(full_text)} 字符")
        
        # 准备文档（取前 4000 字，足够识别结构）
        text_sample = full_text[:4000]
        
        # 如果文档较短，用全文
        if len(full_text) < 4000:
            text_sample = full_text
        
        prompt = f"""你是中国法律文档结构分析专家。

请仔细分析以下法律文档，识别所有的附加内容。

附加内容包括（但不限于）：
- 附件（附件一、附件二等）
- 附表（附表1、附表2等）
- 附录
- 附注
- 注释
- 说明（编者说明、修订说明、立法说明等）
- 附：（后面跟具体内容）
- 其他任何非正文的补充内容

要求：
1. 识别所有附加内容的标题或标识
2. 找出标识附加内容开始的关键文字（用于定位）
3. 判断内容类型（表格/列表/文本说明）
4. 简要描述其作用

返回严格的 JSON 格式：
{{
  "attachments": [
    {{
      "type": "附加内容的完整标题",
      "start_marker": "标识开始的关键文字（5-20字）",
      "content_type": "表格/列表/文本",
      "description": "简要描述"
    }}
  ]
}}

注意：
- 如果没有附加内容，返回 {{"attachments": []}}
- 不要识别"附则"，附则是正文的一部分
- start_marker 必须是文档中实际出现的文字

文档内容：
{text_sample}
"""
        
        try:
            response = Generation.call(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                result_format='message'
            )
            
            if response.status_code == 200:
                result_text = response.output.choices[0].message.content
                
                print(f"   AI 返回: {result_text[:200]}...")
                
                # 提取 JSON（AI 可能返回带说明的文本）
                json_match = re.search(r'\{[\s\S]*\}', result_text)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = json.loads(result_text)
                
                attachments = result.get('attachments', [])
                
                # 为每个附件找到准确的行号（增强版）
                lines = full_text.split('\n')
                
                for att in attachments:
                    marker = att['start_marker']
                    
                    # 策略 1：精确匹配
                    found = False
                    for i, line in enumerate(lines):
                        if marker in line:
                            att['line_num'] = i
                            att['content'] = marker
                            found = True
                            print(f"   ✅ 精确匹配: {marker} → 行 {i}")
                            break
                    
                    if found:
                        continue
                    
                    # 策略 2：拆分匹配（处理换行的情况）
                    marker_parts = marker.split('：')
                    if len(marker_parts) >= 2:
                        first_part = marker_parts[0] + '：'
                        
                        for i, line in enumerate(lines):
                            if first_part in line:
                                att['line_num'] = i
                                att['content'] = first_part
                                found = True
                                print(f"   ✅ 拆分匹配: {first_part} → 行 {i}")
                                break
                    
                    if found:
                        continue
                    
                    # 策略 3：关键词匹配（取前5个字）
                    marker_keywords = marker[:5]
                    for i, line in enumerate(lines):
                        if marker_keywords in line:
                            att['line_num'] = i
                            att['content'] = line.strip()
                            found = True
                            print(f"   ⚠️  关键词匹配: {marker_keywords} → 行 {i}")
                            break
                    
                    if not found:
                        print(f"   ❌ 未找到: {marker}")
                
                print(f"✅ AI 识别到 {len(attachments)} 个附加内容")
                for att in attachments:
                    line_info = att.get('line_num', '?')
                    print(f"   - {att.get('type', '?')} (行号: {line_info})")
                
                return attachments
            
            else:
                print(f"❌ AI 调用失败: {response.code} - {response.message}")
                return []
        
        except Exception as e:
            print(f"❌ AI 识别出错: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def convert_attachment_to_natural_language(self, attachment_text: str, attachment_name: str = "附加内容", attachment_type: str = "表格") -> str:
        """
        将附加内容转换为自然语言描述
        
        Args:
            attachment_text: 附加内容原始文本
            attachment_name: 附加内容名称
            attachment_type: 类型（表格/列表/文本）
            
        Returns:
            natural_text: 自然语言描述
        """
        print(f"\n🤖 AI 转换附加内容为自然语言...")
        print(f"   名称: {attachment_name}")
        print(f"   类型: {attachment_type}")
        print(f"   长度: {len(attachment_text)} 字符")
        
        # 根据类型选择转换策略
        if attachment_type == '表格':
            prompt = f"""你是法律文档处理专家。

请将以下表格转换为清晰的自然语言描述。

要求：
1. 用完整的句子描述表格中的每一行信息
2. 保留所有数据（不能遗漏任何信息）
3. 按逻辑分组分段描述
4. 语言流畅自然，便于理解和检索
5. 如果有备注或说明，在相关描述末尾注明

表格名称：{attachment_name}

原始表格：
{attachment_text}

请输出自然语言描述：
"""
        
        elif attachment_type == '列表':
            prompt = f"""你是法律文档处理专家。

请将以下列表内容转换为完整的句子描述。

要求：
1. 用完整的句子表达每个列表项
2. 保留所有信息
3. 语言流畅自然

列表名称：{attachment_name}

原始列表：
{attachment_text}

请输出自然语言描述：
"""
        
        else:  # 文本类型
            # 文本类型的附加内容，检查格式是否需要优化
            if len(attachment_text) < 200:
                # 短文本，直接返回
                print(f"   ✅ 短文本，保持原样")
                return attachment_text.strip()
            
            prompt = f"""你是法律文档处理专家。

请优化以下文本的格式和表达，使其更清晰易懂。

要求：
1. 保留所有信息
2. 优化段落结构
3. 语言流畅自然

原始文本：
{attachment_text}

请输出优化后的文本：
"""
        
        try:
            response = Generation.call(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                result_format='message'
            )
            
            if response.status_code == 200:
                natural_text = response.output.choices[0].message.content
                
                print(f"   ✅ 转换成功")
                print(f"   转换后长度: {len(natural_text)} 字符")
                print(f"   长度变化: {len(natural_text) - len(attachment_text):+d} 字符")
                
                return natural_text.strip()
            
            else:
                print(f"   ❌ AI 调用失败: {response.code} - {response.message}")
                print(f"   ⚠️  返回原始文本")
                return attachment_text
        
        except Exception as e:
            print(f"   ❌ 转换出错: {e}")
            print(f"   ⚠️  返回原始文本")
            return attachment_text



    def extract_keywords_for_chunk(self, chunk_data: dict) -> dict:
        """
        为分块提取关键词（细粒度 + 标注每条）
        
        Args:
            chunk_data: 分块数据
        
        Returns:
            {
                'keywords': [...],
                'articles_detail': [...],
                'articles_count': 3
            }
        """
        chunk_text = chunk_data.get('chunk_text', '')
        chunk_type = chunk_data.get('chunk_type', 'unknown')
        
        # 附件：整体提取
        if chunk_type == 'attachment':
            keywords = self._extract_keywords_single(chunk_text, max_keywords=12)
            
            return {
                'keywords': keywords,
                'articles_detail': [{
                    'article_number': chunk_data.get('article_start', '附件'),
                    'article_text': chunk_text[:500],  # 只保存前 500 字符
                    'keywords': keywords,
                    'start_pos': 0,
                    'end_pos': len(chunk_text)
                }],
                'articles_count': 1
            }
        
        # 条组：拆分每条单独提取
        elif chunk_type in ['article_group', 'single_article']:
            articles = self._split_articles(chunk_text)
            
            if not articles:
                # 无法拆分，整体提取
                keywords = self._extract_keywords_single(chunk_text, max_keywords=12)
                return {
                    'keywords': keywords,
                    'articles_detail': [{
                        'article_number': chunk_data.get('article_start', ''),
                        'article_text': chunk_text[:500],
                        'keywords': keywords,
                        'start_pos': 0,
                        'end_pos': len(chunk_text)
                    }],
                    'articles_count': 1
                }
            
            # 每条单独提取
            articles_detail = []
            all_keywords = []
            start_pos = 0
            
            for article_info in articles:
                article_number = article_info['number']
                article_text = article_info['text']
                
                # AI 提取关键词
                keywords = self._extract_keywords_single(article_text, max_keywords=8)
                
                articles_detail.append({
                    'article_number': article_number,
                    'article_text': article_text[:500],  # 限制长度
                    'keywords': keywords,
                    'start_pos': start_pos,
                    'end_pos': start_pos + len(article_text)
                })
                
                all_keywords.extend(keywords)
                start_pos += len(article_text) + 2
            
            # 条组整体关键词（去重）
            unique_keywords = list(set(all_keywords))[:20]
            
            return {
                'keywords': unique_keywords,
                'articles_detail': articles_detail,
                'articles_count': len(articles_detail)
            }
        
        else:
            # 其他类型：整体提取
            keywords = self._extract_keywords_single(chunk_text, max_keywords=10)
            return {
                'keywords': keywords,
                'articles_detail': [{
                    'article_number': chunk_data.get('article_start', ''),
                    'article_text': chunk_text[:500],
                    'keywords': keywords,
                    'start_pos': 0,
                    'end_pos': len(chunk_text)
                }],
                'articles_count': 1
            }
    
    def _split_articles(self, text: str) -> list:
        """拆分条文（按"第X条"）"""
        import re
        
        pattern = r'第[零一二三四五六七八九十百千万\d]+条'
        matches = list(re.finditer(pattern, text))
        
        if not matches:
            return []
        
        articles = []
        
        for i, match in enumerate(matches):
            article_number = match.group()
            start = match.end()
            
            if i < len(matches) - 1:
                end = matches[i + 1].start()
            else:
                end = len(text)
            
            article_text = text[start:end].strip()
            
            if article_text:
                articles.append({
                    'number': article_number,
                    'text': article_number + ' ' + article_text
                })
        
        return articles
    
    def _extract_keywords_single(self, text: str, max_keywords: int = 8) -> list:
        """单个文本提取关键词（AI）"""
        
        # 黑名单
        blacklist = ['规定', '应当', '可以', '法律', '内容', '根据', '依照', '不得', '条例', '办法', '本法', '本条', '有关', '相关', '情形', '规定的', '依法', '国家', '人民政府', '主管部门', '部门', '机构', '单位', '人员']
        
        prompt = f"""你是法律条文关键词提取专家。

请从下面这段法律条文中，严格提取 {max_keywords} 个“法律检索关键词”。

【提取目标】
关键词必须优先覆盖以下类型：
1. 法律主体（如：公司、股东、董事、监事、会计人员、纳税人）
2. 法律行为（如：出资、登记、清算、披露、伪造、缴纳）
3. 权利义务（如：出资义务、报告义务、保密义务）
4. 法律责任（如：赔偿责任、行政处罚、罚款、刑事责任）
5. 时间期限（如：三十日、五年、期限届满）
6. 金额比例（如：五十万元、百分之十）
7. 程序要求（如：审批、备案、登记、决议）

【严格要求】
1. 关键词必须直接来自原文，不允许你改写、扩写、解释、概括
2. 每个关键词长度控制在 2-8 个字
3. 不要输出通用空词，例如：规定、应当、可以、本法、有关、相关、依法
4. 不要输出完整句子
5. 不要输出重复关键词
6. 如果原文中没有足够多的高质量关键词，就少输出，不要凑数
7. 返回结果必须是 JSON 数组，不要添加任何解释

【法律条文】
{text[:800]}

【返回示例】
["股东","认缴出资","出资期限","到期债务","提前缴纳"]
"""

        try:
            from dashscope import Generation
            
            response = Generation.call(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                result_format='message'
            )
            
            if response.status_code == 200:
                result = response.output.choices[0].message.content.strip()
                
                # 解析关键词
                keywords = [k.strip() for k in result.split(',') if k.strip()]
                
                # 过滤黑名单
                keywords = [k for k in keywords if k not in blacklist and len(k) >= 2]
                
                # 验证关键词在原文中出现
                keywords = [k for k in keywords if k in text]
                
                # 限制数量
                keywords = keywords[:max_keywords]
                
                return keywords if keywords else []
            
            else:
                return self._extract_keywords_by_rules(text, max_keywords)
        
        except Exception as e:
            return self._extract_keywords_by_rules(text, max_keywords)
    
    def _extract_keywords_by_rules(self, text: str, max_keywords: int = 8) -> list:
        """规则提取关键词（备用）"""
        import re
        
        keyword_patterns = [
            r'劳动合同', r'用人单位', r'劳动者', r'工资', r'社会保险',
            r'试用期', r'解除', r'终止', r'赔偿', r'补偿', r'经济补偿金',
            r'税收', r'税率', r'纳税', r'应纳税额', r'免税',
            r'车船税', r'税目', r'税额', r'计税'
        ]
        
        keywords = []
        for pattern in keyword_patterns:
            if re.search(pattern, text):
                keywords.append(pattern.replace('\\', ''))
        
        keywords = list(set(keywords))[:max_keywords]
        
        return keywords if keywords else []


# 创建全局实例
ai_structure_analyzer = AIStructureAnalyzer()


# 测试代码
if __name__ == '__main__':
    print("AI 结构分析服务已加载")
