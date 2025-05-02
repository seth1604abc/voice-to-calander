from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from service import chat_service

chat_router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str = Field(..., description="User問題")

class ChatResponse(BaseModel):
    data: str = Field(..., description="AI回應")

@chat_router.post("/")
async def send_message(request: ChatRequest):
    """
    發送消息給Claude並獲取回應
    """
    try:
        # 調用服務處理消息
        content = await chat_service.generate_response(message=request.message)
        
        return ChatResponse(
            data=content
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理消息時出錯: {str(e)}")
    
@chat_router.post("/voice")
async def add_schedule(
        audio: UploadFile = File(...),
        timestamp: int = Form(None),
        timezoneName: str = Form(None)):
    try:
        response = await chat_service.reservation_google_calander(file=audio, timezone=timezoneName, send_timestamp=timestamp)
        return {
            "data": response["voice_text"],
            "agent_response": response.get("agent_response", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理消息時出錯: {str(e)}")
