# Nanobot Workspace 機制說明

Nanobot 的 **Workspace (工作區)** 是 Agent 的核心資料儲存目錄，預設位於 `~/.nanobot/workspace`。
它包含了 Agent 的人格設定、記憶、技能以及使用者定義的上下文。

## 1. 目錄結構

```
~/.nanobot/workspace/
├── AGENTS.md       # Agent 定義 (人格、角色)
├── SOUL.md         # 核心準則與行為模式
├── USER.md         # 使用者偏好設定
├── IDENTITY.md     # (可選) 自訂身份識別資訊
├── TOOLS.md        # (可選) 自訂工具說明
├── memory/         # 記憶庫
│   ├── MEMORY.md   # 長期記憶 (由 Agent 自動維護或手動編輯)
│   └── HISTORY.md  # 對話歷史記錄
├── skills/         # 技能目錄 (Python scripts 或 Markdown 說明)
└── media/          # 媒體檔案儲存區 (圖片、語音等)
```

## 2. 核心檔案說明

### 上下文檔案 (Bootstrap Files)

Agent 在每次啟動或對話時，會讀取以下檔案來構建 System Prompt：

- **`AGENTS.md`**: 定義 Agent 的名字、角色描述。
- **`SOUL.md`**: 定義 Agent 的 "靈魂"，包含核心價值觀、說話風格、行為準則。這是調整 Bot 個性最重要的地方。
- **`USER.md`**: 存放關於您的資訊，例如您的名字、偏好、工作習慣等，讓 Agent 更了解您。

### 記憶系統 (Memory)

- **`memory/MEMORY.md`**: 存放重要事實與長期記憶。Agent 會嘗試將對話中的重要資訊總結並寫入此處。
- **`memory/HISTORY.md`**: 存放原始對話記錄。

### 技能與擴充 (Skills & Plugins)

- **`skills/`**: 您可以將 Python 腳本或 Markdown 教學放在這裡。
  - **Python Scripts**: 可透過 `config.json` 的 `tools.custom` 載入為可執行的工具。
  - **Markdown**: 作為知識庫，Agent 可以透過 `read_file` 讀取並學習如何執行特定任務。

## 3. 如何運作

1.  **初始化**: 當您執行 `nanobot onbaord` 時，系統會自動建立此目錄並填入預設範本。
2.  **載入**: 每次對話時，`ContextBuilder` 會讀取這些檔案內容，組合成 LLM 的 System Prompt。
3.  **持久化**: Agent 對檔案系統的操作 (如 `write_file`) 預設限制在此 Workspace 內 (除非設定 `restrict_to_workspace=False`)，以確保安全性。

## 4. 自訂建議

- **修改個性**: 編輯 `SOUL.md`，加入 "你是一個喜歡用表情符號的助手"。
- **增加知識**: 在 `skills/` 下建立 `coding_guidelines.md`，貼上您的團隊程式碼規範。
- **備份**: 整個 Workspace 都是純文字檔，非常適合使用 Git 進行版本控制。
