from urllib.request import Request
from flask import Blueprint, request, make_response
from .model import AnalyticsService

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route("/cmj/", methods=["GET", "POST"])
def analytics_cmj():
    if request.method == "POST":
        try:
            forceFile = request.files.get("forceFile")
            velFile = request.files.get("velocityFile")
            data = AnalyticsService.get_cmj_values(velFile, forceFile)
            resp = make_response(data, 200)
            resp.headers["Content-Type"] = "application/json"
            return resp
        except Exception as err:
            resp = make_response({"message": str(err)}, 500)
            resp.headers["Content-Type"] = "application/json"
            return resp