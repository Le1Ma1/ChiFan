def make_choose_carousel(restaurants, session_id, duration_min=None):
    """
    餐廳清單 Carousel，每張卡片一個投票按鈕＋可顯示投票時限
    """
    bubbles = []
    for idx, r in enumerate(restaurants):
        contents = [
            {"type": "text", "text": f"{r['name']}", "weight": "bold", "size": "xl"},
            {"type": "text", "text": f"餐廳編號：{idx+1}", "size": "sm", "color": "#999999", "margin": "md"},
        ]
        # 新增投票時限說明（可選）
        if duration_min:
            contents.append({"type": "text", "text": f"投票時限：{duration_min} 分鐘", "size": "sm", "color": "#F6B802", "margin": "md"})
        contents.append({
            "type": "button",
            "style": "primary",
            "action": {
                "type": "postback",
                "label": "投我一票",
                "data": f"vote=choose&session={session_id}&index={idx+1}"
            }
        })
        bubbles.append({
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents
            }
        })
    # "隨機選擇"專用 Bubble
    random_contents = [
        {"type": "text", "text": "選擇障礙", "weight": "bold", "size": "xl", "color": "#1E90FF"},
        {"type": "text", "text": "不知道吃哪一家？讓機器人隨機推薦一間！", "size": "sm", "color": "#666666", "wrap": True, "margin": "md"},
    ]
    if duration_min:
        random_contents.append({"type": "text", "text": f"投票時限：{duration_min} 分鐘", "size": "sm", "color": "#F6B802", "margin": "md"})
    random_contents.append({
        "type": "button",
        "style": "primary",
        "color": "#FF8800",
        "action": {
            "type": "postback",
            "label": "幫我隨機選一家",
            "data": f"vote=choose&session={session_id}&index=random"
        }
    })
    random_bubble = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": random_contents
        }
    }
    bubbles.append(random_bubble)
    return {
        "type": "carousel",
        "contents": bubbles
    }

# 票選結果 Flex 不變
def make_choose_result_flex(winner_names, max_vote, all_vote_result):
    win_text = "、".join(winner_names)
    stat_text = "\n".join([f"{name}：{cnt} 票" for name, cnt in all_vote_result])
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "本次最高票餐廳", "weight": "bold", "size": "lg", "color": "#3D82FF"},
                {"type": "text", "text": win_text, "weight": "bold", "size": "xl", "color": "#2ECC40", "margin": "md"},
                {"type": "text", "text": f"最高 {max_vote} 票", "size": "sm", "color": "#999999", "margin": "md"},
                {"type": "separator", "margin": "lg"},
                {"type": "text", "text": "全部投票結果：", "weight": "bold", "size": "sm", "margin": "md"},
                {"type": "text", "text": stat_text, "size": "sm", "margin": "sm", "wrap": True}
            ]
        }
    }
