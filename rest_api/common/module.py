import json
import re
from bson import ObjectId
from flask.helpers import make_response
from werkzeug.wrappers import response

class Result:
    def __init__(self,
                 json_message, 
                 http_code) -> None:
        self.json_message = json_message
        self.http_code = http_code


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
            if isinstance(o, ObjectId):
                return str(o)
            return json.JSONEncoder.default(self, o)

def validateMongoFilter(filter: dict):
    for key, value in filter.items():
        if("$" in key or "$" in value):
            return False
        if("==" in key or "==" in value):
            return False
    return True

    
def addCORSHeader(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:9000"
    return response