"""
向量化服务
调用 DashScope Embeddings API 将文本转为向量
"""

from dashscope import TextEmbedding
import dashscope
import os
import time
from typing import List, Union


class EmbeddingService:
    """向量化服务：将文本转为 1536 维向量"""
    
    def __init__(self):
        # 设置 API Key
        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if not dashscope.api_key:
            raise ValueError("未设置 DASHSCOPE_API_KEY 环境变量")
        
        # 配置参数
        self.model = TextEmbedding.Models.text_embedding_v1
        self.batch_size = 25  # DashScope 最多支持 25 个文本/批次
        self.max_retries = 3  # 最大重试次数
        self.retry_delay = 2  # 重试延迟（秒）
        
        print(f"✅ 向量化服务初始化成功")
        print(f"   模型: {self.model}")
        print(f"   批次大小: {self.batch_size}")
    
    def get_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        获取文本的向量嵌入（支持单个或批量）
        
        Args:
            texts: 单个文本或文本列表
            
        Returns:
            向量列表 [[向量1], [向量2], ...]
            每个向量是 1536 维的浮点数列表
        """
        # 统一处理为列表
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            return []
        
        print(f"\n🧬 开始向量化...")
        print(f"   文本数量: {len(texts)}")
        
        all_embeddings = []
        
        # 分批处理
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(texts) + self.batch_size - 1) // self.batch_size
            
            print(f"   处理批次 {batch_num}/{total_batches}（{len(batch)} 个文本）...")
            
            # 调用 API（带重试）
            batch_embeddings = self._get_embeddings_with_retry(batch)
            
            if batch_embeddings:
                all_embeddings.extend(batch_embeddings)
                print(f"      ✅ 批次 {batch_num} 完成")
            else:
                print(f"      ❌ 批次 {batch_num} 失败")
                raise Exception(f"批次 {batch_num} 向量化失败")
        
        print(f"   ✅ 向量化完成：{len(all_embeddings)} 个向量")
        
        # 验证向量维度
        if all_embeddings:
            vector_dim = len(all_embeddings[0])
            print(f"   ✅ 向量维度: {vector_dim}")
            
            if vector_dim != 1536:
                print(f"      ⚠️  警告：向量维度不是 1536！")
        
        return all_embeddings
    
    def _get_embeddings_with_retry(self, texts: List[str]) -> List[List[float]]:
        """
        调用 API 获取向量（带重试机制）
        
        Args:
            texts: 文本列表
            
        Returns:
            向量列表
        """
        for attempt in range(self.max_retries):
            try:
                response = TextEmbedding.call(
                    model=self.model,
                    input=texts
                )
                
                if response.status_code == 200:
                    # 提取向量
                    embeddings = [item['embedding'] for item in response.output['embeddings']]
                    return embeddings
                else:
                    error_msg = response.message if hasattr(response, 'message') else '未知错误'
                    print(f"      ⚠️  API 返回错误（尝试 {attempt + 1}/{self.max_retries}）: {error_msg}")
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                    else:
                        raise Exception(f"API 调用失败: {error_msg}")
                        
            except Exception as e:
                print(f"      ⚠️  API 调用异常（尝试 {attempt + 1}/{self.max_retries}）: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise Exception(f"API 调用失败: {str(e)}")
        
        return []
    
    def get_single_embedding(self, text: str) -> List[float]:
        """
        获取单个文本的向量（便捷方法）
        
        Args:
            text: 单个文本
            
        Returns:
            1536 维向量
        """
        embeddings = self.get_embeddings([text])
        return embeddings[0] if embeddings else []
    
    def test_connection(self) -> bool:
        """
        测试 API 连接是否正常
        
        Returns:
            True 表示连接正常
        """
        try:
            print("\n🔍 测试 DashScope Embeddings API 连接...")
            
            test_text = "这是一个测试文本"
            embedding = self.get_single_embedding(test_text)
            
            if embedding and len(embedding) == 1536:
                print(f"   ✅ API 连接正常")
                print(f"   ✅ 向量维度: {len(embedding)}")
                print(f"   ✅ 向量示例: [{embedding[0]:.6f}, {embedding[1]:.6f}, ..., {embedding[-1]:.6f}]")
                return True
            else:
                print(f"   ❌ API 返回数据异常")
                return False
                
        except Exception as e:
            print(f"   ❌ API 连接失败: {str(e)}")
            return False


# 创建全局实例
embedding_service = EmbeddingService()


# 测试代码
if __name__ == '__main__':
    print("\n" + "="*60)
    print("向量化服务测试")
    print("="*60)
    
    # 测试连接
    if embedding_service.test_connection():
        print("\n✅ 向量化服务可用！")
        
        # 测试批量向量化
        print("\n🧪 测试批量向量化...")
        test_texts = [
            "劳动者有下列情形之一的，用人单位可以解除劳动合同",
            "用人单位应当按照劳动合同约定和国家规定，向劳动者及时足额支付劳动报酬",
            "劳动合同期满的，劳动合同终止"
        ]
        
        embeddings = embedding_service.get_embeddings(test_texts)
        
        if len(embeddings) == len(test_texts):
            print(f"   ✅ 批量向量化成功：{len(embeddings)} 个向量")
            print(f"   ✅ 每个向量维度: {len(embeddings[0])}")
        else:
            print(f"   ❌ 批量向量化失败")
    else:
        print("\n❌ 向量化服务不可用，请检查 DASHSCOPE_API_KEY")

