from flask import Blueprint, request, jsonify
from flask.wrappers import Request


trainings_bp = Blueprint('trainings', __name__)

@trainings_bp.route("/", methods=['GET', 'POST'])
def trainings():
    if request.method == 'GET':
        trainingsGet()
        return jsonify(
            user_id=10,
            first_name="szymon",
            last_name="karpecki"
        )
    else:
        trainingsPost()
        return "post"

def trainingsGet():
    print("requested_get")

def trainingsPost():
    print("trainings_post")
