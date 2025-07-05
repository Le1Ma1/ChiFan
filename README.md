# ChiFan

解決「今天要吃什麼」的 LINE 機器人小幫手
```
ChiFan/
│
├── .env.example        # 範例環境變數（存放API金鑰，不要推到公開repo）
├── requirements.txt    # 依賴套件列表（pip install -r requirements.txt）
├── README.md           # 專案說明文件
├── run.py              # 專案啟動入口（Flask主程式）
│
├── app/                # 主程式碼資料夾
│   ├── __init__.py         # Flask APP組裝、藍圖註冊
│   │
│   ├── flex/               # Flex Message 樣板與回傳生成
│   │   ├── list_carousel.py    # 多店家列表 Carousel Flex 樣板
│   │   ├── vote_card.py       # 投票卡片 Flex 樣板
│   │   └── __init__.py        # 讓 flex 變成 package，可空
│   │
│   ├── services/             # 後端邏輯/資料處理
│   │   ├── db.py             # 與 Supabase（雲端資料庫）連線、CRUD
│   │   ├── line_api.py       # 跟 LINE 官方API互動的封裝
│   │   └── __init__.py       # 讓 services 變成 package，可空
│   │
│   ├── utils/                # 工具函式與主 webhook（藍圖）邏輯
│   │   ├── main.py           # webhook 接收事件與訊息分派（主控制邏輯）
│   │   ├── commands.py       # 處理指令或訊息解析的函式
│   │   └── __init__.py       # 讓 utils 變成 package，可空
│   │
│   └── migrations/           # 資料表結構（SQL檔案）
│       └── 001_init.sql      # 初始資料表結構建立語法
│
├── migrations/           # <可選> 若後續需要獨立migration，可放其他SQL檔
│   └── 001_init.sql
│
└── tests/                # 未來可用於自動化測試的程式
```