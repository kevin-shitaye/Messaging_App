from enum import unique
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime

from sqlalchemy.orm import backref
from settings import *


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =SQLALCHEMY_DATABASE_URI


db = SQLAlchemy(app)




class Users(db.Model):
    user_id = db.Column(db.String, primary_key=True, unique=True)
    username = db.Column(db.String, nullable=False)
    profile_picture = db.Column(db.String, nullable=True)
    

    def __init__(self, user_id, username, profile_picture):
        self.user_id = user_id
        self.username = username
        self.profile_picture = profile_picture


    def serialize(self):
        return{
            "user_id":self.user_id,
            "username":self.username,
            "profile_picture":self.profile_picture
        }

    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self.user_id)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.String, db.ForeignKey('users.user_id'))
    reciever_id = db.Column(db.String, db.ForeignKey('users.user_id'))
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime)
    read = db.Column(db.Boolean)

    def __init__(self, sender_id, reciever_id, content, read=False, timestamp=datetime.datetime.now()):
        self.sender_id = sender_id
        self.reciever_id = reciever_id
        self.content = content
        self.timestamp = timestamp
        self.read = read

    def serialize(self):
        return {
            "id":self.id,
            "sender_id":self.sender_id,
            "reciever_id":self.reciever_id,
            "content":self.content,
            "timestamp": self.timestamp,
            "read":self.read
        }

# db.drop_all()
# db.create_all()