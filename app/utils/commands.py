def parse_command(text):
    """可用於未來分辨用戶輸入的指令格式"""
    if text.startswith("/add "):
        return "add", text[5:]
    return "unknown", text
