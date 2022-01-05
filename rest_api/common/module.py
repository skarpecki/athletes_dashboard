import json
from bson import ObjectId

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