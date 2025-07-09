def build_restaurant_list(restaurants):
    """回傳 Carousel Flex Message json"""
    # 假設 restaurants: List[Dict]
    columns = []
    for r in restaurants:
        columns.append({
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": r["name"], "weight": "bold", "size": "xl"},
                    {"type": "text", "text": r["address"], "size": "sm", "color": "#888888"}
                ]
            }
        })
    return {
        "type": "carousel",
        "contents": columns
    }

def make_del_carousel(restaurants, group_id):
    """
    顯示可刪除餐廳的 Flex Carousel，每家餐廳一個刪除按鈕
    """
    bubbles = []
    for r in restaurants:
        bubbles.append({
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": r['name'], "weight": "bold", "size": "xl"},
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#FF4444",
                        "action": {
                            "type": "postback",
                            "label": "刪除",
                            "data": f"vote=del&session=menu&name={r['name']}"
                        }
                    }
                ]
            }
        })
    return {
        "type": "carousel",
        "contents": bubbles
    }
