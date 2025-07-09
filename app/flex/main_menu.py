def make_main_menu_flex():
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "請選擇操作", "weight": "bold", "size": "xl", "margin": "md"},
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#009900",
                    "margin": "lg",
                    "action": {
                        "type": "postback",
                        "label": "今天吃什麼",
                        "data": "menu=choose"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "color": "#FF4444",
                    "margin": "md",
                    "action": {
                        "type": "postback",
                        "label": "刪除餐廳",
                        "data": "menu=del"
                    }
                }
            ]
        }
    }
