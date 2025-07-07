from dotenv import load_dotenv
from app.polling import start_polling_job

load_dotenv()
start_polling_job()

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("="*60)
    print("🍚 ChiFan LINE Bot 啟動！")
    print("http://localhost:5000")
    print("="*60)
    app.run(port=5000, debug=True)