# ChiFan

解決「今天要吃什麼」的 LINE 機器人小幫手
```
ChiFan/
│
├── .env                      # 範例環境變數（存放API金鑰 , 不要推到公開repo）
├── requirements.txt          # 依賴套件列表（pip install -r requirements.txt）
├── README.md                 # 專案說明文件
├── run.py                    # 專案啟動入口（Flask主程式）
│      
├── app/                      # 主程式碼資料夾
│   ├── __init__.py           # Flask APP組裝、藍圖註冊
│   │  
│   ├── flex/                 # Flex Message 樣板與回傳生成
│   │   ├── list_carousel.py  # 多店家列表 Carousel Flex 樣板
│   │   ├── vote_card.py      # 投票卡片 Flex 樣板
│   │   ├── choose_flex.py      
│   │   ├── main_menu.py      
│   │   ├── tiebreak_flex.py      
│   │   └── __init__.py       # 讓 flex 變成 package , 可空
│   │
│   ├── services/             # 後端邏輯/資料處理
│   │   ├── vote_service.py   # 票選相關指令
│   │   ├── db.py             # 與 Supabase（雲端資料庫）連線、CRUD
│   │   └── __init__.py       # 讓 services 變成 package , 可空
│   │
│   ├── main.py               # webhook 接收事件與訊息分派（主控制邏輯）
│   ├── polling.py            # APScheduler 定時任務 , 投票自動結算
│   │
│   └── migrations/           # (備份) 起初開發測試用 , 當前主要使用雲端數據庫 Supabase
│       └── 001_init.sql      
│
├── init_db.py                # ※(本地測試用 , 已棄用) 早期用來初始化 SQLite 本地資料庫的腳本
├── chifan.db                 # ※(本地測試用 , 已棄用) 早期使用 SQLite 產生的資料庫檔案
│
└── tests/                    # 未來可用於自動化測試的程式
```