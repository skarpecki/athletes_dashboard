import re
from flask import Flask, request
from flask.helpers import make_response
from pymongo import MongoClient

app = Flask(__name__)
app.config["FLASK_ENV"] = "development"

from resource_trainings.controller import trainings_bp
app.register_blueprint(trainings_bp, url_prefix="/trainings")

from resource_exercises.controller import exercises_bp
app.register_blueprint(exercises_bp, url_prefix="/exercises")

from resource_analytics.controller import analytics_bp
app.register_blueprint(analytics_bp, url_prefix="/analytics")

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.before_request
def handle_options_request():
    if(request.method == "OPTIONS"):
        return make_response()

@app.after_request
def add_cors_header(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS";
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0')
