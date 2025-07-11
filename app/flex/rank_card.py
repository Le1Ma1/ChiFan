def make_topuser_flex(topuser):
    # topuser: {"name": "張三", "count": 6, "desc": "本月投票王"}
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {"type": "text", "text": "😎 用戶貢獻榜", "weight": "bold", "size": "xl"},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": f"恭喜 {topuser['name']}！", "weight": "bold", "size": "md", "margin": "md"},
                {"type": "text", "text": f"{topuser['desc']}", "size": "sm", "color": "#666666", "wrap": True, "margin": "md"},
                {"type": "text", "text": f"已累積 {topuser['count']} 次投票/新增紀錄，社群最佳貢獻～", "size": "sm", "wrap": True, "margin": "md"}
            ]
        }
    }

def make_top3_flex(top3):
    """
    產生本群組人氣排行TOP3 Flex
    top3: List[Dict]，每筆資料需含 name, votes
    例如：
    [
        {"name": "八方雲集", "votes": 12},
        {"name": "麥當勞", "votes": 8},
        {"name": "燒肉丼飯", "votes": 6}
    ]
    """
    colors = ["#FFD700", "#C0C0C0", "#CD7F32"]  # 金銀銅
    items = [
        {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": f"#{i+1}",
                    "weight": "bold",
                    "size": "lg",
                    "color": colors[i] if i < len(colors) else "#888888",
                    "flex": 1
                },
                {
                    "type": "text",
                    "text": f"{item['name']}",
                    "weight": "bold",
                    "size": "md",
                    "flex": 3
                },
                {
                    "type": "text",
                    "text": f"{item['votes']} 票",
                    "size": "sm",
                    "color": "#888888",
                    "align": "end",
                    "flex": 2
                },
            ]
        }
        for i, item in enumerate(top3)
    ]

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "🏆 本群組人氣排行 TOP 3",
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "separator",
                    "margin": "md"
                },
            ] + items + [
                {
                    "type": "text",
                    "text": "趕快發起投票，讓你喜歡的餐廳衝上榜！",
                    "size": "xs",
                    "color": "#888888",
                    "margin": "md"
                }
            ]
        }
    }
