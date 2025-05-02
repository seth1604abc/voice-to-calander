import httpx
from typing import Optional, Dict, Any
from config import config

class ClaudeClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ClaudeClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.api_key = config["CLAUDE_API_KEY"]
        self.model = "claude-3-5-sonnet-20240620"

        self.client = httpx.AsyncClient(
            timeout=30.0,
            base_url="https://api.anthropic.com",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
        )
        self._initialized = True

    # async def ensure_client(self):
    #     """確保異步客戶端已初始化"""
    #     if self.client is None:
    #         self.client = httpx.AsyncClient(
    #             timeout=30.0,
    #             base_url="https://api.anthropic.com",
    #             headers={
    #                 "x-api-key": self.api_key,
    #                 "anthropic-version": "2023-06-01",
    #                 "content-type": "application/json"
    #             }
    #         )

    async def generate_text(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> Dict[Any, Any]:
        """
        使用Claude API生成文本回應
        
        Args:
            prompt: 提示文本
            max_tokens: 最大生成令牌數
            temperature: 生成溫度，控制創造性

        Returns:
            包含API回應的字典
        """
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = await self.client.post(url="/v1/messages", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": str(e)}
        
# async def get_claude_client() -> ClaudeClient:
#     client = ClaudeClient()
#     await client.ensure_client()
#     return client

async def get_claude_client() -> ClaudeClient:
    return ClaudeClient()