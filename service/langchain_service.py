from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain import hub
from typing import Dict, Any
import json
from .googlecalander import google_calander_service
from config import config

# Define tool input schemas
# class GoogleCalendarEventInput(BaseModel):
#     """Input for creating a Google Calendar event."""
#     summary: str = Field(..., description="Event title/summary")
#     description: str = Field(..., description="Event description")
#     start_time: str = Field(..., description="Start time in ISO format with timezone")
#     end_time: str = Field(..., description="End time in ISO format with timezone")
#     timezone: str = Field(..., description="Timezone for the event")

@tool
def create_calendar_event(event_data: str) -> str:
    """
    Creates an event in Google Calendar.
    
    Args:
        event_data: A JSON string containing event details with fields:
            - summary: The title of the event
            - description: Event description  
            - start_time: Start time in ISO format
            - end_time: End time in ISO format
            - timezone: Timezone (default: Asia/Taipei)
    
    Returns:
        str: Success message with event link or error message
    """
    data = json.loads(event_data)
    try:
        event_dict = {
            "summary": data.get("summary", ""),
            "description": data.get("description", ""),
            "start": {
                "dateTime": data.get("start_time"),
                "timeZone": data.get("timezone", "Asia/Taipei")
            },
            "end": {
                "dateTime": data.get("end_time"),
                "timeZone": data.get("timezone", "Asia/Taipei")
            }
        }
        
        event = google_calander_service.create_event(event_dict)
        return f"Event created successfully: {event.get('htmlLink', 'No link available')}"
    except Exception as e:
        return f"Error creating calendar event: {str(e)}"

class LangChainService:
    def __init__(self):
        self.llm = ChatAnthropic(
            model=config.get("CLAUDE_MODEL", "claude-3-5-sonnet-20240620"),
            anthropic_api_key=config["CLAUDE_API_KEY"],
            temperature=0.7
        )
        
        # Define tools
        self.tools = [
            create_calendar_event
        ]
        
        # Set up memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.prompt = hub.pull("hwchase17/react")
        
        # Create agent with ReAct framework which works better with Claude
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )
    
    async def process_message(self, message: str) -> str:
        """Process a text message using the LangChain agent."""
        try:
            response = await self.agent_executor.ainvoke({"input": message})
            return response["output"]
        except Exception as e:
            return f"Error processing message: {str(e)}"
    
    async def process_audio(self, transcribed_text: str, timestamp: int, timezone: str) -> Dict[str, Any]:
        """
        Process an audio file using the LangChain agent.
        Let the LLM decide how to use the tools to accomplish the task.
        """
        try:
            agent_response = await self.agent_executor.ainvoke({
                "input": f"""
                我有一段語音內容需要處理並創建日曆事件。

                語音轉錄內容："{transcribed_text}"

                當前時間戳：{timestamp}
                時區：{timezone}

                請幫我分析這段內容，提取事件詳情（標題、描述、開始和結束時間），並在Google日曆中創建對應的事件。
                如果內容中缺少某些信息，請友好的回覆缺少哪些重要訊息，再讓使用者補上（例如，如果只提到時間，可以請使用者補上做甚麼事情）。
                重要的事情有：時間、地點、事件名稱

                完成後，請提供一個友好的回應，告訴我事件已創建，並包含事件的詳細信息。
                """
            })
            
            return {
                "voice_text": transcribed_text,
                "agent_response": agent_response["output"]
            }
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error processing audio: {error_details}")
            return {
                "error": f"Error processing audio: {str(e)}",
                "voice_text": "無法轉錄音頻"
            }

# Create a singleton instance
langchain_service = LangChainService()
