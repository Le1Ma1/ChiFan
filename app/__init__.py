from flask import Flask
from app.main import webhook_blueprint

def create_app():
    app = Flask(__name__)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    return app
