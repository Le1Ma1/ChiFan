from dotenv import load_dotenv
load_dotenv()

from app import create_app
app = create_app()

if __name__ == "__main__":
    print("="*60)
    print("🍚 ChiFan LINE Bot 啟動！")
    print("http://localhost:5000")
    print("="*60)
    app.run(port=5000, debug=True)