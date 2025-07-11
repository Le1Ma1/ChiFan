def make_help_card():
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {"type": "text", "text": "📖 功能說明", "weight": "bold", "size": "xl"},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text":
                    "大部分功能都可直接點主選單操作。\n"
                    "只有『新增餐廳』需手動輸入：\n\n"
                    "    /add 餐廳名稱\n\n"
                    "（例：/add 八方雲集）\n\n"
                    "其他如票選、刪除餐廳、說明查詢、聯絡作者，都可直接按主選單進行！",
                    "size": "sm", "wrap": True, "margin": "md"
                },
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": "有問題請點主選單『聯絡作者』", "size": "xs", "color": "#888888", "margin": "md"}
            ]
        }
    }
