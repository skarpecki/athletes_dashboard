from app import db
from enum import Enum
from marshmallow import fields, Schema


class UserSchema(Schema):
    """User Schema"""

    userID = fields.Integer(attribute='id')
    mailAddress = fields.String(attribute='mail_address')
    password = fields.String(attribute='password')

class User(db.Model):
    """User model class"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    mail_address = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)