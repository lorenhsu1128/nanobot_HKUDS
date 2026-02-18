# Nanobot Plugin System Guide

Nanobot 支援透過外掛系統擴充功能，目前主要支援 **Custom Tools (自訂工具)**。

## 1. Custom Tools (自訂工具)

您可以編寫自己的 Python 類別作為工具，並讓 Nanobot 載入使用。

### 步驟 1: 建立工具類別

建立一個 Python檔案 (例如 `my_tools.py`)，並定義一個繼承自 `nanobot.agent.tools.base.Tool` 的類別。

```python
from nanobot.agent.tools.base import Tool

class StockPriceTool(Tool):
    name = "get_stock_price"
    description = "Get the current price of a stock."
    parameters = {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "The stock symbol (e.g., AAPL)"
            }
        },
        "required": ["symbol"]
    }

    async def execute(self, symbol: str) -> str:
        # 實作您的邏輯，例如呼叫外部 API
        price = 150.00  # 假資料
        return f"The price of {symbol} is ${price}"
```

### 步驟 2: 設定 Config

在您的 Nanobot 設定檔 (例如 `~/.nanobot/config.json`) 中，將該工具的 **完整 Import Path** 加入 `tools.custom` 清單。

確保 `my_tools.py` 在 Python 的 `PYTHONPATH` 中，或者直接放在 Nanobot 的工作目錄下。

```json
{
  "tools": {
    "custom": ["my_tools.StockPriceTool"]
  }
}
```

### 步驟 3: 使用

啟動 Nanobot 後，Agent 將會自動載入該工具，並在需要時調用它。

## 2. Channels (通訊頻道)

目前的 Channel 系統也支援動態載入，但需要註冊在 `nanobot/channels/manager.py` 的 `CHANNEL_REGISTRY` 中。未來將開放更彈性的註冊機制。
