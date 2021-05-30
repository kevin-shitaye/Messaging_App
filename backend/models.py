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
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    profile_picture = db.Column(db.String, nullable=True)
    

    def __init__(self, username, password):
        self.username = username
        self.password = password


    def serialize(self):
        return{
            "user_id":self.user_id,
            "username":self.username,
            "profile_picture":self.profile_picture
        }


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_username = db.Column(db.String(20), db.ForeignKey('users.username'))
    reciever_username = db.Column(db.String(20), db.ForeignKey('users.username'))
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime)
    read = db.Column(db.Boolean)

    def __init__(self, sender_username, reciever_username, content, read=False, timestamp=datetime.datetime.now()):
        self.sender_username = sender_username
        self.reciever_username = reciever_username
        self.content = content
        self.timestamp = timestamp
        self.read = read

    def serialize(self):
        return {
            "id":self.id,
            "sender_username":self.sender_username,
            "reciever_username":self.reciever_username,
            "content":self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y,  %I:%M %p"),
            "read":self.read
        }



