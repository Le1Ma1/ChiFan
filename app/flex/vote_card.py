def build_vote_card(name, votes, total):
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": f"建議：{name}", "weight": "bold"},
                {"type": "text", "text": f"已投票：{votes}/{total}", "color": "#aaaaaa"}
            ]
        }
    }
