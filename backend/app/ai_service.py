import dashscope
from dashscope import Generation
import os
from typing import List, Dict

# 设置 API Key
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

class AIService:
    """通义千问 AI 服务"""
    
    def __init__(self):
        self.model = "qwen-turbo"  # 使用 qwen-turbo 模型
    
    def chat(self, messages: List[Dict[str, str]], user_message: str) -> str:
        """
        发送消息到通义千问获取回复
        
        Args:
            messages: 历史消息列表 [{"role": "user", "content": "..."}, ...]
            user_message: 当前用户消息
            
        Returns:
            AI 回复内容
        """
        try:
            # 构建消息历史（最多保留最近10条）
            conversation_history = []
            
            # 添加系统提示 #
            conversation_history.append({
                "role": "system",
                "content": "你是内控AI法律咨询助手，专门回答劳动法、合同法、公司法等相关问题。请用专业、清晰、友好的语气回答用户问题。"
            })
            
            # 添加历史消息（最近10条）
            for msg in messages[-10:]:
                conversation_history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # 添加当前消息
            conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # 调用通义千问 API
            response = Generation.call(
                model=self.model,
                messages=conversation_history,
                result_format='message'
            )
            
            # 检查响应
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                return f"抱歉，AI 服务暂时不可用。错误码: {response.status_code}"
                
        except Exception as e:
            return f"抱歉，处理您的请求时出现错误: {str(e)}"
    
    def test_connection(self) -> bool:
        """测试 API 连接"""
        try:
            response = Generation.call(
                model=self.model,
                messages=[{"role": "user", "content": "你好"}],
                result_format='message'
            )
            return response.status_code == 200
        except:
            return False

# 创建全局 AI 服务实例
ai_service = AIService()
