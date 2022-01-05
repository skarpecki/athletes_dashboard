from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)
app.config["FLASK_ENV"] = "development"

from resource_trainings.controller import trainings_bp
app.register_blueprint(trainings_bp, url_prefix='/trainings')

from resource_exercises.controller import exercises_bp
app.register_blueprint(exercises_bp, url_prefix='/exercises')

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    app.run()