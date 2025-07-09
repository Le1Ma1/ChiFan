# app/flex/vote_card.py

def make_vote_card(title, desc, vote_type, session_id):
    """
    回傳一個投票卡片的 Flex Message dict
    :param title: 餐廳名稱
    :param desc: 票選說明
    :param vote_type: add / del
    :param session_id: 對應投票 session , 用於 postback data
    """
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": title, "weight": "bold", "size": "xl", "margin": "md"},
                {"type": "text", "text": desc, "size": "sm", "color": "#999999", "wrap": True, "margin": "md"},
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "md",
                    "margin": "lg",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#2ECC40",
                            "action": {
                                "type": "postback",
                                "label": "同意",
                                "data": f"vote={vote_type}&session={session_id}&value=1"
                            }
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "color": "#FF4136",
                            "action": {
                                "type": "postback",
                                "label": "不同意",
                                "data": f"vote={vote_type}&session={session_id}&value=0"
                            }
                        }
                    ]
                }
            ]
        }
    }
