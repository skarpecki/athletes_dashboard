import re
from flask import Flask, request
from flask.helpers import make_response
from pymongo import MongoClient
import yaml
from os import path
from flask_sqlalchemy import SQLAlchemy

def load_config():
    if path.exists(path.dirname(path.abspath(__file__)) + '/../config/app.conf.yaml'):
        config_file_path = path.dirname(path.abspath(__file__)) + '/../config/app.conf.yaml'
    elif path.exists(path.dirname(path.abspath(__file__)) + '/../config/default.conf.yaml'):
        config_file_path = path.dirname(path.abspath(__file__)) + '/../config/default.conf.yaml'
    else:
        raise FileNotFoundError("Config file not found.")

    with open(config_file_path) as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
        return config

db = SQLAlchemy()
app = Flask(__name__)
config = load_config()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.before_request
def handle_options_request():
    if(request.method == "OPTIONS"):
        return make_response()

@app.after_request
def add_cors_header(response):
    response.headers["Access-Control-Allow-Origin"] = config["APP"]["ACCESS-CONTROL-ALLOW-ORIGIN"]
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    print(response.headers["Access-Control-Allow-Origin"])
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response

def create_app(test_config=None):
    config = load_config()
    app.config["FLASK_ENV"] = "development"
    app.config['SQLALCHEMY_DATABASE_URI'] = ("mysql+pymysql"
                                            f"://{config['MYSQL_DATABASE']['USER']}"
                                            f":{config['MYSQL_DATABASE']['PASSWORD']}"
                                            f"@{config['MYSQL_DATABASE']['HOST']}"
                                            f"/{config['MYSQL_DATABASE']['DB_NAME']}")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = "FALSE"

    from app.resource_trainings.controller import trainings_bp
    app.register_blueprint(trainings_bp, url_prefix="/trainings")

    from app.resource_exercises.controller import exercises_bp
    app.register_blueprint(exercises_bp, url_prefix="/exercises")

    from app.resource_analytics.controller import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix="/analytics")

    return app