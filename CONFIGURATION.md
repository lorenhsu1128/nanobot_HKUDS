# Nanobot 配置說明 (Configuration Guide)

本文件詳細說明 `config.json` 中的各項設定欄位。所有的設定值都對應到 `nanobot/config/schema.py` 中的 Pydantic 模型。

## 1. Agents 設定 (`agents`)

設定 Agent 的預設行為與參數。

| 欄位 (Key)                   | 類型   | 預設值                      | 說明                                                      |
| :--------------------------- | :----- | :-------------------------- | :-------------------------------------------------------- |
| `defaults.workspace`         | string | `~/.nanobot/workspace`      | Agent 的工作目錄路徑 (支援 `~` 展開)。                    |
| `defaults.model`             | string | `anthropic/claude-opus-4-5` | 預設使用的 LLM 模型名稱 (LiteLLM 格式)。                  |
| `defaults.maxTokens`         | int    | `8192`                      | LLM生成回應的最大 token 數。                              |
| `defaults.temperature`       | float  | `0.7`                       | LLM 的隨機性 (0.0 為最確定，1.0 為最有創意)。             |
| `defaults.maxToolIterations` | int    | `20`                        | 單次對話中，Agent 連續使用工具的最大次數 (防止無窮迴圈)。 |
| `defaults.memoryWindow`      | int    | `50`                        | 觸發記憶固化 (Consolidation) 的對話訊息數量閾值。         |

## 2. 通道設定 (`channels`)

設定各個聊天平台的連接參數。

### Telegram (`channels.telegram`)

| 欄位        | 類型      | 預設    | 說明                                                                    |
| :---------- | :-------- | :------ | :---------------------------------------------------------------------- |
| `enabled`   | bool      | `false` | 是否啟用 Telegram 通道。                                                |
| `token`     | string    | `""`    | Telegram Bot Token (從 @BotFather 取得)。                               |
| `allowFrom` | list[str] | `[]`    | 允許互動的使用者 ID 或使用者名稱清單 (白名單)。空陣列表示不允許任何人。 |
| `proxy`     | string    | `null`  | (選用) HTTP/SOCKS5 代理伺服器網址。                                     |

### Discord (`channels.discord`)

| 欄位         | 類型      | 預設        | 說明                                          |
| :----------- | :-------- | :---------- | :-------------------------------------------- |
| `enabled`    | bool      | `false`     | 是否啟用 Discord 通道。                       |
| `token`      | string    | `""`        | Discord Bot Token。                           |
| `allowFrom`  | list[str] | `[]`        | 允許互動的使用者 ID 清單。                    |
| `gatewayUrl` | string    | `wss://...` | Discord Gateway URL。                         |
| `intents`    | int       | `37377`     | Bot 需要的權限整數 (預設包含訊息讀取與發送)。 |

### Slack (`channels.slack`)

| 欄位                | 類型      | 預設        | 說明                                                                                           |
| :------------------ | :-------- | :---------- | :--------------------------------------------------------------------------------------------- |
| `enabled`           | bool      | `false`     | 是否啟用 Slack 通道。                                                                          |
| `mode`              | string    | `"socket"`  | 連線模式 (目前僅支援 Socket Mode)。                                                            |
| `botToken`          | string    | `""`        | Bot User OAuth Token (`xoxb-`).                                                                |
| `appToken`          | string    | `""`        | App-Level Token (`xapp-`).                                                                     |
| `userTokenReadOnly` | bool      | `true`      | 是否僅使用 Bot Token 讀取。                                                                    |
| `groupPolicy`       | string    | `"mention"` | 群組/頻道中的觸發策略: `"mention"` (被標記時), `"open"` (所有訊息), `"allowlist"` (指定頻道)。 |
| `groupAllowFrom`    | list[str] | `[]`        | `groupPolicy` 為 `"allowlist"` 時，允許的 Channel ID。                                         |
| `dm.enabled`        | bool      | `true`      | 是否啟用私訊功能。                                                                             |
| `dm.policy`         | string    | `"open"`    | 私訊策略: `"open"` (所有人), `"allowlist"` (指定用戶)。                                        |

### Email (`channels.email`)

支援透過 IMAP/SMTP 進行郵件互動。

| 欄位                   | 類型        | 說明                                            |
| :--------------------- | :---------- | :---------------------------------------------- |
| `enabled`              | bool        | 是否啟用。                                      |
| `consentGranted`       | bool        | **必須為 true** 才能啟用 (確認擁有信箱存取權)。 |
| `imapHost`, `imapPort` | string, int | IMAP 伺服器設定 (接收郵件)。                    |
| `smtpHost`, `smtpPort` | string, int | SMTP 伺服器設定 (發送郵件)。                    |
| `pollIntervalSeconds`  | int         | 檢查新郵件的間隔秒數 (預設 30)。                |
| `allowFrom`            | list[str]   | 允許互動的寄件者 Email 地址白名單。             |

**(WhatsApp 設定類似，需搭配外部 Bridge 使用)**

## 3. 模型供應商 (`providers`)

設定 LLM API 金鑰與端點。Nanobot 使用 LiteLLM，支援大多數供應商。

| 供應商 (Key)                                            | 欄位           | 說明                                                     |
| :------------------------------------------------------ | :------------- | :------------------------------------------------------- |
| `openai`, `anthropic`, `openrouter`, `deepseek`, `groq` | `apiKey`       | API 金鑰。                                               |
| `vllm`, `ollama`, `llamacpp`                            | `apiBase`      | (選用) 自定義 API 基礎網址 (例如用於 Local LLM 或代理)。 |
| (通用)                                                  | `extraHeaders` | (選用) 自定義 HTTP Headers。                             |

### 本地端 LLM設定範例

若要使用 Ollama 或 Llama.cpp，請在 `providers` 中設定 API Base，並在 `agents.defaults.model` 中指定對應的模型名稱。

**Ollama 範例**:

- `providers.ollama.apiBase`: `"http://localhost:11434"`
- `agents.defaults.model`: `"ollama/llama3"`

**Llama.cpp 範例**:

- `providers.llamacpp.apiBase`: `"http://localhost:8080/v1"`
- `agents.defaults.model`: `"openai/llama-3-8b-instruct"` (因為 Llama.cpp 主要相容 OpenAI 格式)

**注意**: API Key 建議透過環境變數 (如 `NANOBOT_PROVIDERS__OPENAI__API_KEY`) 設定，以避免寫入設定檔造成洩漏。

## 4. 閘道設定 (`gateway`)

設定 Nanobot Gateway Server 的監聽位址。

| 欄位   | 類型   | 預設        | 說明                                  |
| :----- | :----- | :---------- | :------------------------------------ |
| `host` | string | `"0.0.0.0"` | 監聽位址 (0.0.0.0 表示接受所有連線)。 |
| `port` | int    | `18790`     | 監聽埠號。                            |

## 5. 工具設定 (`tools`)

設定 Agent 可用工具的權限與參數。

| 欄位                    | 類型   | 預設    | 說明                                                                         |
| :---------------------- | :----- | :------ | :--------------------------------------------------------------------------- |
| `restrictToWorkspace`   | bool   | `false` | **安全設定**: 若為 `true`，則檔案操作工具僅能存取 `workspace` 目錄下的檔案。 |
| `web.search.apiKey`     | string | `""`    | Brave Search API Key (用於網路搜尋)。                                        |
| `web.search.maxResults` | int    | `5`     | 搜尋結果最大筆數。                                                           |
| `exec.timeout`          | int    | `60`    | Shell 指令執行的超時秒數。                                                   |
| `mcpServers`            | dict   | `{}`    | [MCP (Model Context Protocol)](https://modelcontextprotocol.io) 伺服器設定。 |

### MCP Server 設定範例

```json
"mcpServers": {
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]
  },
  "chrome-devtools": {
    "command": "npx",
    "args": ["-y", "chrome-devtools-mcp@latest"]
  }
}
```
