from flask import Blueprint, request, make_response
from .model import ExerciseService
import json

exercises_bp = Blueprint('exercises', __name__)


@exercises_bp.route("/", methods=['GET', 'POST'])
def exercises():
    if request.method == 'GET':
        filter = request.args
        result = ExerciseService(r"mongodb://localhost:27017",
                                "dashboard",
                                "exercises").get_exercises(filter)
    else:
        exercise_json = request.get_json(force=True)
        result = ExerciseService(r"mongodb://localhost:27017",
                                  "dashboard",
                                  "exercises").insert_exercise(exercise_json)
    resp = make_response(result.json_message, result.http_code)
    resp.headers["Content-Type"] = "application/json"
    resp.headers["Access-Control-Allow-Origin"] = "http://localhost:9000"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp    



@exercises_bp.route("/<exercise_id>", methods=['GET', 'PUT'])
def exercise(exercise_id):
    if request.method == 'GET':
        result = ExerciseService(r"mongodb://localhost:27017",
                                "dashboard",
                                "exercises").get_exercise(exercise_id)
        resp = make_response(result.json_message, result.http_code)
        resp.headers["Content-Type"] = "application/json"
        resp.headers["Access-Control-Allow-Origin"] = "http://localhost:9000"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return resp 
