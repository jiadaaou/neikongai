import os
import json
import re
from typing import Any, Dict, List

import dashscope
from dashscope import Generation

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")


class QueryUnderstandingService:
    """用户问题理解层：把自然语言问题转成结构化 query_profile"""

    def __init__(self):
        self.model = "qwen-turbo"
        self.allowed_question_types = [
            "合规咨询", "是否合法判断", "材料要求", "制度缺口检查",
            "审批流程咨询", "风险分析", "处罚后果", "未知"
        ]
        self.allowed_business_stages = ["事前", "事中", "事后", "未知"]
        self.allowed_business_domains = [
            "财务", "税务", "车辆税务", "采购", "合同", "用工",
            "资金", "车辆", "印章", "档案", "治理", "未知"
        ]

    def understand_query(self, user_query: str, company_context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        user_query = (user_query or "").strip()
        company_context = company_context or {}

        if not user_query:
            return self._empty_result(user_query)

        prompt = self._build_prompt(user_query, company_context)

        try:
            response = Generation.call(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是企业依法合规系统中的“用户问题理解器”。"
                            "你的任务不是回答问题，而是把用户问题转成结构化检索对象。"
                            "你必须只输出 JSON，不要输出解释。"
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                result_format="message",
            )

            if response.status_code != 200:
                return self._apply_rule_fixes(user_query, self._empty_result(user_query))

            content = response.output.choices[0].message.content
            parsed = self._parse_json(content)
            normalized = self._normalize_result(user_query, parsed)
            return self._apply_rule_fixes(user_query, normalized)

        except Exception:
            return self._apply_rule_fixes(user_query, self._empty_result(user_query))

    def _build_prompt(self, user_query: str, company_context: Dict[str, Any]) -> str:
        return f"""请把用户问题转成结构化 query_profile，只输出 JSON。

固定字段：
{{
  "question_type": "",
  "business_stage": "",
  "business_domain": "",
  "subject": "",
  "behavior": "",
  "objects": [],
  "scenario": "",
  "company_level": "",
  "department": "",
  "time_scope": "",
  "region": "",
  "keywords": [],
  "negative_keywords": [],
  "retrieval_query": "",
  "needs_enterprise_kb": true,
  "needs_law_kb": true,
  "confidence": 0.0
}}

规则：
1. question_type 只能从以下值中选择：
["合规咨询","是否合法判断","材料要求","制度缺口检查","审批流程咨询","风险分析","处罚后果","未知"]

2. business_stage 只能从以下值中选择：
["事前","事中","事后","未知"]

3. business_domain 只能从以下值中选择：
["财务","税务","采购","合同","用工","资金","车辆","印章","档案","治理","未知"]

4. keywords 只保留 3-8 个中文短词
5. retrieval_query 必须是一句适合知识库检索的话
6. 若用户问题中已明确出现具体税种（如车船税、车辆购置税、增值税、企业所得税），不得替换成其他税种
7. 若出现“车船税”，business_domain 优先判断为“车辆税务”或“税务”，keywords 与 retrieval_query 必须保留“车船税”
8. 不确定时填“未知”或空数组，不得编造
9. 只输出合法 JSON

企业上下文：
{json.dumps(company_context, ensure_ascii=False)}

用户问题：
{user_query}
"""

    def _parse_json(self, content: str) -> Dict[str, Any]:
        content = (content or "").strip()
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

    def _normalize_result(self, original_query: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "original_query": original_query,
            "question_type": self._pick_enum(parsed.get("question_type"), self.allowed_question_types, "未知"),
            "business_stage": self._pick_enum(parsed.get("business_stage"), self.allowed_business_stages, "未知"),
            "business_domain": self._pick_enum(parsed.get("business_domain"), self.allowed_business_domains, "未知"),
            "subject": self._clean_text(parsed.get("subject")),
            "behavior": self._clean_text(parsed.get("behavior")),
            "objects": self._clean_list(parsed.get("objects")),
            "scenario": self._clean_text(parsed.get("scenario")),
            "company_level": self._clean_text(parsed.get("company_level")),
            "department": self._clean_text(parsed.get("department")),
            "time_scope": self._clean_text(parsed.get("time_scope")),
            "region": self._clean_text(parsed.get("region")),
            "keywords": self._clean_keywords(parsed.get("keywords")),
            "negative_keywords": self._clean_keywords(parsed.get("negative_keywords")),
            "retrieval_query": self._clean_text(parsed.get("retrieval_query")) or original_query,
            "needs_enterprise_kb": bool(parsed.get("needs_enterprise_kb", True)),
            "needs_law_kb": bool(parsed.get("needs_law_kb", True)),
            "confidence": self._clean_confidence(parsed.get("confidence")),
        }
        return result

    def _empty_result(self, original_query: str) -> Dict[str, Any]:
        return {
            "original_query": original_query,
            "question_type": "未知",
            "business_stage": "未知",
            "business_domain": "未知",
            "subject": "",
            "behavior": "",
            "objects": [],
            "scenario": "",
            "company_level": "",
            "department": "",
            "time_scope": "",
            "region": "",
            "keywords": [],
            "negative_keywords": [],
            "retrieval_query": original_query,
            "needs_enterprise_kb": True,
            "needs_law_kb": True,
            "confidence": 0.0,
        }

    def _pick_enum(self, value: Any, allowed: List[str], default: str) -> str:
        value = self._clean_text(value)
        return value if value in allowed else default

    def _clean_text(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def _clean_list(self, value: Any) -> List[str]:
        if not isinstance(value, list):
            return []
        cleaned: List[str] = []
        for item in value:
            text = self._clean_text(item)
            if text and text not in cleaned:
                cleaned.append(text)
        return cleaned[:8]

    def _clean_keywords(self, value: Any) -> List[str]:
        items = self._clean_list(value)
        return items[:8]

    def _clean_confidence(self, value: Any) -> float:
        try:
            num = float(value)
        except Exception:
            return 0.0
        if num < 0:
            return 0.0
        if num > 1:
            return 1.0
        return num

    def _apply_rule_fixes(self, original_query: str, result: Dict[str, Any]) -> Dict[str, Any]:
        q = original_query or ""

        if "车船税" in q:
            result["business_domain"] = "车辆税务"
            result["question_type"] = result["question_type"] if result["question_type"] != "未知" else "合规咨询"
            kws = result.get("keywords", [])
            if "车船税" not in kws:
                kws = ["车船税"] + kws
            if "车辆" in q and "车辆" not in kws:
                kws.append("车辆")
            if "公司" in q and "公司" not in kws:
                kws.append("公司")
            result["keywords"] = kws[:8]
            result["retrieval_query"] = "公司车辆车船税纳税义务、纳税主体、申报缴纳要求"

        if "车辆购置税" in q:
            result["business_domain"] = "车辆税务"
            kws = result.get("keywords", [])
            if "车辆购置税" not in kws:
                kws = ["车辆购置税"] + kws
            result["keywords"] = kws[:8]
            result["retrieval_query"] = "公司购买应税车辆是否需要缴纳车辆购置税、纳税主体、申报要求"

        if "是否需要" in q or "要不要" in q:
            if result.get("question_type") == "未知":
                result["question_type"] = "合规咨询"

        return result


query_understanding_service = QueryUnderstandingService()
