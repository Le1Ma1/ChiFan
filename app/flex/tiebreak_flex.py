def make_tiebreak_flex(winner_names, session_id):
    buttons = []
    for name in winner_names:
        buttons.append({
            "type": "button",
            "style": "primary",
            "margin": "md",
            "action": {
                "type": "postback",
                "label": name,
                "data": f"tiebreak={session_id}&winner={name}"
            }
        })
    # 隨機決定按鈕
    buttons.append({
        "type": "button",
        "style": "secondary",
        "margin": "md",
        "action": {
            "type": "postback",
            "label": "隨機決定",
            "data": f"tiebreak={session_id}&winner=random"
        }
    })
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "票選平手決選", "weight": "bold", "size": "xl", "margin": "md"},
                {"type": "text", "text": "請選擇最終決策的餐廳，或讓系統隨機決定", "size": "sm", "margin": "md"},
            ] + buttons
        }
    }
