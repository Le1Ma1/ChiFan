from linebot.models import TextSendMessage

def reply_text(line_bot_api, event, text):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))
