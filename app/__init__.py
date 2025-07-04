from flask import Flask
from .utils.main import webhook_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(webhook_blueprint, url_prefix="/callback")
    return app
