from config import config
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from router import chat_router

os.environ["PATH"] += os.pathsep + config["FFMPEG_BIN_PATH"]

app = FastAPI(
    title="語音記帳系統",
    description="使用FastAPI、LangChain和Claude API構建的語音記帳系統",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/assets", StaticFiles(directory="static_files"), name="assets")
templates = Jinja2Templates(directory="template")

@app.get("/")
def health_check():
    """健康檢查端點"""
    return {
        "status": "ok"
    }

@app.get("/home")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

app.include_router(chat_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=config["HOST"], 
        port=config["PORT"], 
        reload=config["DEBUG"]
    )