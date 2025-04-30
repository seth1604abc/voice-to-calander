import os
from typing import Dict
import pickle
from pydantic import BaseModel, ValidationError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from config import config

class EventTime(BaseModel):
    dateTime: str
    timeZone: str

class Event(BaseModel):
    summary: str
    description: str
    start: EventTime
    end: EventTime

class GoogleCalanderService:
    def __init__(self, credential_path: str, token_path: str):
        self.SCOPES = ["https://www.googleapis.com/auth/calendar"]
        self.credential_path = credential_path
        self.token_path = token_path
        self.service = self.__get_calendar_service()

    def __get_calendar_service(self) -> Resource:
        """獲取已授權的 Google Calendar API 服務"""
        creds = None
        
        # 嘗試從 token 檔案讀取憑證
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # 如果沒有憑證或憑證已過期
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credential_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # 保存憑證以備後用
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('calendar', 'v3', credentials=creds)
    
    def create_event(self, event: Dict):
        try:
            event_model = Event(**event)
            event_dict = event_model.model_dump()
            event = self.service.events().insert(calendarId="primary", body=event_dict).execute()
            return event
        except ValidationError as e:
            raise ValueError(str(e))
        except HttpError as error:
            print(f'創建事件時發生錯誤: {error}')
            raise

google_calander_service = GoogleCalanderService(credential_path=config["GOOGLE_CALANDER_CREDENTIAL_PATH"], token_path="token.pickle")
