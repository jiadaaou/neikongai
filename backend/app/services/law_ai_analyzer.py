import os
import json
import re
from typing import Dict, Any

import dashscope
from dashscope import Generation


dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")


class LawAIAnalyzer:
    """法律条文 AI 合规单元分析服务"""

    def __init__(self):
        self.model = "qwen-turbo"

    def analyze_chunk(self, chunk_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        输入一条法律 chunk，输出 AI 合规单元
        """
        chunk_text = (chunk_data.get("chunk_text") or "").strip()
        article_start = chunk_data.get("article_start")
        document_title = chunk_data.get("document_title") or ""
        chunk_id = chunk_data.get("chunk_id")

        if not chunk_text:
            return self._empty_result(chunk_id, article_start)

        prompt = self._build_prompt(
            document_title=document_title,
            article_start=article_start,
            chunk_text=chunk_text,
        )

        try:
            response = Generation.call(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是企业内控与法律合规分析专家。你只能基于给定法律条文做结构化提取，不得编造。必须输出 JSON。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                result_format="message"
            )

            if response.status_code != 200:
                result = self._empty_result(chunk_id, article_start)
                result["analysis_status"] = "failed"
                result["raw_ai_output"] = {
                    "status_code": response.status_code,
                    "message": getattr(response, "message", "AI调用失败")
                }
                return result

            content = response.output.choices[0].message.content
            parsed = self._parse_json(content)

            result = {
                "chunk_id": chunk_id,
                "source_article": article_start,
                "subject": self._clean_text(parsed.get("subject")),
                "behavior": self._clean_text(parsed.get("behavior")),
                "obligation": self._clean_text(parsed.get("obligation")),
                "prohibition": self._clean_text(parsed.get("prohibition")),
                "risk_type": self._clean_text(parsed.get("risk_type")),
                "risk_level": self._clean_risk_level(parsed.get("risk_level")),
                "compliance_action": self._clean_text(parsed.get("compliance_action")),
                "keywords": self._clean_keywords(parsed.get("keywords")),
                "analysis_model": self.model,
                "analysis_status": "completed",
                "raw_ai_output": parsed,
            }
            return result

        except Exception as e:
            result = self._empty_result(chunk_id, article_start)
            result["analysis_status"] = "failed"
            result["raw_ai_output"] = {"error": str(e)}
            return result

    def _build_prompt(self, document_title: str, article_start: str, chunk_text: str) -> str:
        return f"""请严格基于下面提供的法律条文，提取企业合规分析结果。
不要扩写，不要解释，不要输出多余文字，只输出 JSON。

输出字段固定为：
{{
  "subject": "义务主体，尽量简短",
  "behavior": "行为/事项，尽量简短",
  "obligation": "该条要求做什么，没有则为空字符串",
  "prohibition": "该条禁止什么，没有则为空字符串",
  "risk_type": "风险类型，没有则为空字符串",
  "risk_level": "高/中/低，如无法判断填低",
  "compliance_action": "企业应采取的合规动作，没有则为空字符串",
  "keywords": ["关键词1", "关键词2", "关键词3"]
}}

要求：
1. 只能根据条文本身提取
2. keywords 最多 5 个，必须是中文短词
3. 不确定时留空，不得编造
4. 必须返回合法 JSON

法律名称：{document_title}
条号：{article_start}

法律条文：
{chunk_text}
"""

    def _parse_json(self, content: str) -> Dict[str, Any]:
        content = content.strip()

        try:
            return json.loads(content)
        except Exception:
            pass

        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass

        return {}

    def _clean_text(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def _clean_keywords(self, value: Any) -> list:
        if not value:
            return []
        if isinstance(value, list):
            cleaned = []
            for item in value:
                item = str(item).strip()
                if item and item not in cleaned:
                    cleaned.append(item)
            return cleaned[:5]
        return []

    def _clean_risk_level(self, value: Any) -> str:
        value = str(value or "").strip()
        if value in {"高", "中", "低"}:
            return value
        return "低"

    def _empty_result(self, chunk_id: Any, article_start: Any) -> Dict[str, Any]:
        return {
            "chunk_id": chunk_id,
            "source_article": article_start,
            "subject": "",
            "behavior": "",
            "obligation": "",
            "prohibition": "",
            "risk_type": "",
            "risk_level": "低",
            "compliance_action": "",
            "keywords": [],
            "analysis_model": self.model,
            "analysis_status": "pending",
            "raw_ai_output": {},
        }


law_ai_analyzer = LawAIAnalyzer()
