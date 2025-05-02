# 語音行程預約系統

這是一個基於 FastAPI、LangChain 和 Claude API 構建的語音行程預約系統，可以將語音轉換為文字，解析文字內容，並自動在 Google Calendar 中創建事件。

## 功能特點

- **語音轉文字**：使用 Whisper 模型將上傳的語音檔案轉換為文字
- **智能解析**：使用 Claude API 解析文字內容，提取事件詳情（標題、描述、時間等）
- **Google Calendar 整合**：自動在 Google Calendar 中創建事件
- **記憶功能**：使用 LangChain 的記憶組件保存對話歷史，提供更連貫的體驗
- **工具化架構**：將功能模組化為 LangChain 工具，由 LLM 自主決定調用順序

## 技術架構

### 核心組件

- **FastAPI**：提供 Web API 服務
- **LangChain**：提供 LLM 工具調用和記憶功能
- **Anthropic Claude API**：提供自然語言理解和生成能力
- **Whisper**：提供語音轉文字功能
- **Google Calendar API**：提供日曆事件管理功能

### 系統流程

1. 用戶上傳語音檔案
2. Whisper 模型將語音轉換為文字
3. LangChain 代理使用 Claude API 解析文字內容，提取事件詳情
4. LangChain 代理調用 Google Calendar API 創建事件
5. 系統返回處理結果和事件詳情

### 目錄結構

```
.
├── config/             # 配置文件
│   ├── __init__.py
│   ├── config.py       # 主配置模塊
│   └── file/           # 配置相關文件（如 Google API 憑證）
├── core/               # 核心功能模塊
│   ├── __init__.py
│   ├── claude.py       # Claude API 客戶端
│   └── whisper.py      # Whisper 語音轉文字模塊
├── router/             # API 路由
│   ├── __init__.py
│   └── chat.py         # 聊天和語音處理路由
├── service/            # 業務邏輯服務
│   ├── __init__.py
│   ├── chat.py         # 聊天服務
│   ├── googlecalander.py  # Google Calendar 服務
│   └── langchain_service.py  # LangChain 集成服務
├── static/             # 靜態文件
├── template/           # 前端模板
│   └── index.html      # 主頁面
├── .env.dev            # 開發環境變量
├── .gitignore          # Git 忽略文件
├── env.example         # 環境變量示例
├── main.py             # 應用入口
├── README.md           # 項目說明文檔
└── requirements.txt    # 依賴包列表
```

## LangChain 集成

本系統使用 LangChain 框架實現以下功能：

### 1. 工具化架構

將核心功能封裝為 LangChain 工具：

- `create_calendar_event`：在 Google Calendar 中創建事件

### 2. 代理決策

使用 LangChain 的 ReAct 代理框架，讓 LLM 自主決定工具調用順序和參數，而不是硬編碼的流程。

### 3. 記憶功能

使用 `ConversationBufferMemory` 保存對話歷史，使系統能夠參考之前的交互，提供更連貫的體驗。

## 安裝與設置

### 前置需求

- Python 3.8+
- FFmpeg（用於音頻處理）
- Google Calendar API 憑證
- Anthropic Claude API 密鑰

1. 設置 Google Calendar API：

- 在 [Google Cloud Console](https://console.cloud.google.com/) 創建項目
- 啟用 Google Calendar API
- 創建 OAuth 2.0 憑證
- 下載憑證 JSON 文件並放入 `config/file/` 目錄

### 運行應用

```bash
python main.py
```

應用將在 http://localhost:3000 運行。

## 使用方法

1. 打開瀏覽器訪問 http://localhost:3000/home
2. 點擊「開始錄音」按鈕，說出您想要安排的事件（例如：「明天早上九點開會」）
3. 點擊「停止錄音」按鈕
4. 點擊「發送到 Claude」按鈕
5. 系統將處理您的語音，創建事件，並顯示結果
