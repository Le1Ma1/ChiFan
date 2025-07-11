def make_vote_guide_card():
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {"type": "text", "text": "🗳️ 發起投票", "weight": "bold", "size": "xl"},
                {"type": "separator", "margin": "md"},
                {
                    "type": "text",
                    "text": (
                        "1️⃣ 請先將本機器人邀請進你的群組\n"
                        "2️⃣ 在群組點擊主選單功能（如「今天吃什麼」、「刪除餐廳」）即可發起投票\n"
                        "\n"
                        "※ 新增餐廳請在群組手動輸入：\n"
                        "   /add 餐廳名稱\n"
                        "   例：/add 八方雲集\n"
                        "\n"
                        "投票匿名且公開透明，結果自動公布！"
                    ),
                    "size": "sm",
                    "wrap": True,
                    "margin": "md"
                }
            ]
        }
    }
