from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app( config_class = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    from app.routes import app_blueprint as app_blueprint
    app.register_blueprint(app_blueprint)

    return app




