def make_contact_card():
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "👨‍💻 聯絡作者",
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "text",
                    "text": "有任何建議、合作或技術問題歡迎來信：",
                    "size": "sm",
                    "color": "#555555",
                    "margin": "md",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": "leimai2023@gmail.com",
                    "weight": "bold",
                    "size": "md",
                    "color": "#1A73E8",
                    "margin": "md"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "action": {
                        "type": "uri",
                        "label": "直接寄信",
                        "uri": "mailto:leimai2023@gmail.com"
                    }
                }
            ]
        }
    }
