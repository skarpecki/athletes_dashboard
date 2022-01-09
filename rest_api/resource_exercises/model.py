from json import dump
import re
from typing import Collection
from typing_extensions import Required
from bson.objectid import ObjectId
from marshmallow import Schema, fields, validate
from enum import Enum
from marshmallow.exceptions import ValidationError
from pymongo import MongoClient, collection
import pymongo
from pymongo.errors import DuplicateKeyError, PyMongoError
from common.module import Result, JSONEncoder, validateMongoFilter


class ExerciseType(Enum):
    STRENGTH = 1
    CARDIO = 2
    SPEED = 3


class Exercise:
    """ Resource representing defined exercise
    
    :param _id: unique identifier
    :param name: name of the exercise (e.g. Deadlift)
    :param type: STRENGHT, CONDITIONING, SPEED
    :param viedo_url: optional url of video presenting exercise
    :param description: generic description of exercise
    :param athletes_descriptions: <key, value> of description for particular athlete
            who may need additional explanation e.g. <12345: "Lorem ipsum dolor..."> 
    """
    def __init__(self,
                 _id,
                 name,
                 type,
                 video_url=None,
                 description=None,
                 athletes_descriptions=None) -> None:
        self._id = _id
        self.name = name
        self.type = ExerciseType(type)
        self.video_url = video_url
        self.description = description
        self.athletes_descriptions = athletes_descriptions
    

class ExerciseSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, error="Empty name not allowed"))
    type = fields.Str(validate=[validate.OneOf([type.name for type in ExerciseType]),
                                validate.Length(min=1, error="Empty type not allowed")])
    video_url = fields.URL(required=False)
    description = fields.Str(required=False)
    athletes_descriptions = fields.Dict(keys=fields.Str(),
                                          values=fields.Str(),
                                          required=False)


class ExerciseService:
    def __init__(self, 
                 db_url, 
                 db_name, 
                 collection_name) -> None:
        self.client = MongoClient(db_url)
        self.db_name = db_name
        self.collection_name = collection_name
    
    def insert_exercise(self, exercise_json: dict):
        try:
            ExerciseSchema().load(data=exercise_json)
            db = self.client['dashboard']
            collection = db['exercises']
            inserted_id = collection.insert_one(exercise_json).inserted_id
            return Result(JSONEncoder().encode(inserted_id), 200)
        except ValidationError as err:
            return Result(err.messages, 400)
        except DuplicateKeyError as err:
            return Result(err._message, 409)
        except PyMongoError as err:
            return (err._message, 400)


    def get_exercises(self, filter={}):
        db = self.client[self.db_name]
        collection = db[self.collection_name]
        if(not validateMongoFilter(filter)):
            return Result({"message": "not allowed sign found in query parameters"}, 400)
        # setting collation to strenght 2 in order to make case insensitive comparison
        document = list(collection.find(filter).collation( {"locale": "en", "strength": 2}))
        return Result(JSONEncoder().encode({"exercises": document}), 200)

    def get_exercise(self, _id):
        db = self.client[self.db_name]
        collection = db[self.collection_name]
        document = collection.find_one(ObjectId(_id))
        return Result(JSONEncoder().encode(document), 200)

