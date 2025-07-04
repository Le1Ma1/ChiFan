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
