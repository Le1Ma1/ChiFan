def make_donate_card():
    return {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://i.postimg.cc/GhNYPv3W/USDT-QR.png",  # 你的 USDT QR 圖片
            "size": "full",
            "aspectRatio": "1:1",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "🌱 支持 ChiFan 開發",
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "text",
                    "text": (
                        "隨著技術不斷進化，開發與維運都需持續投入資源。"
                        "歡迎捐贈表達你的支持，讓系統更穩定、升級更快速！"
                    ),
                    "size": "sm",
                    "wrap": True,
                    "color": "#666666"
                },
                {
                    "type": "separator",
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": "USDT (TRC-20) 地址：",
                    "size": "sm",
                    "weight": "bold",
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": "TUmegztKiXNjhmifi7wJ8SdMkowY2s7Avw", 
                    "size": "md",
                    "color": "#00B900",
                    "margin": "md",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": "(點擊長按此串即可複製)",
                    "size": "xs",
                    "color": "#888888",
                    "margin": "sm"
                }
            ]
        }
    }
