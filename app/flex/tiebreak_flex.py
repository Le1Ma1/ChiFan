def make_tiebreak_flex(winners_name, session_id):
    actions = []
    for name in winners_name:
        actions.append({
            "type": "button",
            "style": "primary",
            "color": "#00B900",
            "action": {
                "type": "postback",
                "label": name,
                "data": f"action=tiebreak&sid={session_id}&win={name}"
            }
        })
    # 加一個隨機
    actions.append({
        "type": "button",
        "style": "secondary",
        "action": {
            "type": "postback",
            "label": "隨機選擇",
            "data": f"action=tiebreak&sid={session_id}&win=random"
        }
    })
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "平票決選",
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "text",
                    "text": "請於 5 分鐘內選擇最終餐廳 , 逾時將自動隨機",
                    "size": "sm",
                    "color": "#555555",
                    "wrap": True,
                    "margin": "md"
                }
            ] + actions
        }
    }
