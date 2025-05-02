from fastapi import HTTPException, UploadFile
from core import get_claude_client, whisper_model
from typing import Dict, Any
from .googlecalander import google_calander_service
from .langchain_service import langchain_service
import os
import aiofiles
from uuid import uuid4
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ChatService:
    def __init__(self):
        pass

    async def generate_response(self, message: str):
        """
        使用LangChain處理消息，利用記憶功能和工具
        """
        try:
            # 使用LangChain處理消息
            response = await langchain_service.process_message(message)
            return response
        except Exception as e:
            # 如果LangChain失敗，回退到原始Claude實現
            claude_client = await get_claude_client()
            response = await claude_client.generate_text(prompt=message)
            return self.get_content(response=response)
    
    def get_content(self, response: Dict[Any, Any]):
        content = ''
        try:
            content = response.get("content", [{}])[0].get("text", "無回應內容")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"處理消息時出錯: {str(e)}")
        
        return content
    
    async def transfer_voice_data(self, file: UploadFile):
        file_id = str(uuid4())
        temp_audio_path = f"{BASE_DIR}\\{file_id}.wav"
        # 保存上傳的文件
        async with aiofiles.open(temp_audio_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        # 使用Whisper進行語音轉文字
        result = whisper_model.transcribe(temp_audio_path)
        transcribed_text = result["text"]
        
        return transcribed_text, temp_audio_path
    
    async def reservation_google_calander(self, file: UploadFile, timezone: str, send_timestamp: int):
        """
        使用LangChain處理語音預約，利用記憶功能和工具
        """
        try:
            # 保存語音文件並獲取文本
            voice_content, temp_audio_path = await self.transfer_voice_data(file=file)
            
            # 使用LangChain處理語音預約
            response = await langchain_service.process_audio(
                transcribed_text=voice_content,
                timestamp=send_timestamp,
                timezone=timezone
            )
            
            # 清理臨時文件
            try:
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
            except Exception as e:
                print(f"無法刪除臨時文件: {e}")
            
            # 如果有錯誤，回退到原始實現
            if "error" in response:
                return await self._legacy_reservation_google_calander(
                    voice_content=voice_content,
                    timezone=timezone,
                    send_timestamp=send_timestamp
                )
            
            return {
                "voice_text": response.get("voice_text", voice_content),
                "agent_response": response.get("agent_response", "")
            }
        except Exception as e:
            # 如果LangChain失敗，回退到原始實現
            voice_content, temp_audio_path = await self.transfer_voice_data(file=file)
            
            # 清理臨時文件
            try:
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
            except Exception as file_e:
                print(f"無法刪除臨時文件: {file_e}")
                
            return await self._legacy_reservation_google_calander(
                voice_content=voice_content,
                timezone=timezone,
                send_timestamp=send_timestamp
            )
    
    async def _legacy_reservation_google_calander(self, voice_content: str, timezone: str, send_timestamp: int):
        """原始的Google Calendar預約實現，作為備用"""
        prompt = f"""
        當前Timestamp: {send_timestamp}
        當前Timezone: {timezone}
        以下是使用者說的話，請將其分析為 Google Calendar 的事件 JSON 格式，包含標題、開始結束時間、時區，並自動補充缺少的合理資訊（如預設持續 1 小時）：

        原始句子：
        「{voice_content}」

        範例：
        輸入：「明天早上九點開會」
        輸出：
        {{
            "summary": "開會",
            "description": "使用者提到的會議",
            "start": {{
                "dateTime": "2025-05-01T09:00:00+08:00",
                "timeZone": "{timezone}"
            }},
            "end": {{
                "dateTime": "2025-05-01T10:00:00+08:00",
                "timeZone": "{timezone}"
            }}
        }}

        請以以下JSON格式回傳（不需要解釋）：
        {{
            "summary": "...",
            "description": "...",
            "start": {{
                "dateTime": "...",
                "timeZone": "..."
            }},
            "end": {{
                "dateTime": "...",
                "timeZone": "..."
            }}
        }}
        """

        response = await self.generate_response(message=prompt)
        event_dict = json.loads(response)
        event = google_calander_service.create_event(event_dict)
        return {
            "voice_text": voice_content
        }
        
    
chat_service = ChatService()
