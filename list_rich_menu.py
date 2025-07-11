from linebot.v3.messaging import MessagingApi
from linebot.v3.webhooks import Configuration

config = Configuration(access_token='ZEpProhkMOgeqXxO5K1r9x/t8Ey3ZTA27LvxrQn1K9Mu8fI5ejOhkiNClW8ce71wqL/DymwV4QhFQ5R6yhbVImSMQbYRtl5oSREcoAWYUR8ctNbTvmzZ73+JM37o3i/8sdpSdWp9MLn59QmAvPi74AdB04t89/1O/w1cDnyilFU=')
api = MessagingApi(config)

def list_rich_menus():
    resp = api.get_rich_menu_list()
    for menu in resp.rich_menus:
        print(f"rich_menu_id: {menu.rich_menu_id} | 名稱: {menu.name}")

if __name__ == "__main__":
    list_rich_menus()
