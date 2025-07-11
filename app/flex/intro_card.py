def make_intro_card():
    return {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://i.postimg.cc/htNVbTsJ/LINE-intro.png",
            "size": "full",
            "aspectRatio": "16:9",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "🍱 ChiFan 群組投票機器人",
                    "weight": "bold",
                    "size": "xl",
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": "讓吃飯決策不再糾結，大家一起開心投票選美食！",
                    "size": "md",
                    "wrap": True,
                    "color": "#666666"
                },
                {
                    "type": "separator",
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "text",
                            "text": "✨ 主要功能",
                            "weight": "bold",
                            "size": "md"
                        },
                        {
                            "type": "text",
                            "text": (
                                "• 餐廳新增/刪除群組票選\n"
                                "• 今日吃什麼一鍵投票\n"
                                "• 匿名公平，減少爭吵\n"
                                "• 平票時自動協助決選"
                            ),
                            "size": "sm",
                            "wrap": True
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "spacing": "md",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#00B900",
                    "action": {
                        "type": "postback",
                        "label": "🏆 人氣排行",
                        "data": "action=top3"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "postback",
                        "label": "😎 貢獻榜",
                        "data": "action=topuser"
                    }
                }
            ]
        }
    }
