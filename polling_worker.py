import os
from dotenv import load_dotenv

load_dotenv()  # 確保 .env 變數可讀取

from app.polling import start_polling_job

if __name__ == "__main__":
    start_polling_job()
    print("Polling worker started!")
    import time
    while True:
        time.sleep(10)
