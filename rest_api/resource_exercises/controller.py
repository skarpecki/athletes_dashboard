from flask import Blueprint, request, make_response
from .model import ExerciseService
import json

exercises_bp = Blueprint('exercises', __name__)


@exercises_bp.route("/", methods=['GET', 'POST'])
def exercises():
    if request.method == 'GET':
        return exercisesGet()
    else:
        return exercisesPost(request.get_json(force=True))

@exercises_bp.route("/<exercise_id>", methods=['GET', 'PUT'])
def exercise(exercise_id):
    if request.method == 'GET':
        return exerciseGetByID(exercise_id)

def exercisesGet(filter={}):
    result = ExerciseService(r"mongodb://localhost:27017",
                                "dashboard",
                                "exercises").get_exercises(filter)
    resp = make_response(result.json_message, result.http_code)
    resp.headers["mimetype"] = "application/json"
    return resp

def exerciseGetByID(exercise_id):
    result = ExerciseService(r"mongodb://localhost:27017",
                                "dashboard",
                                "exercises").get_exercise(exercise_id)
    resp = make_response(result.json_message, result.http_code)
    resp.headers["mimetype"] = "application/json"
    return resp 

def exercisesPost(exercise_json):
    result = ExerciseService(r"mongodb://localhost:27017",
                                  "dashboard",
                                  "exercises").insert_exercise(exercise_json)
    resp = make_response(result.json_message, result.http_code)
    resp.headers["mimetype"] = "application/json"
    return resp


