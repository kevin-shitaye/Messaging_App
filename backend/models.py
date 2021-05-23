from enum import unique
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./app.db'
db = SQLAlchemy(app)
app.secret_key = 'SECRET'



class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    profile_picture = db.Column(db.String)
    

    def __init__(self, username, password, profile_picture=None):
        self.username = username
        self.password = password
        #bettter if its the address of the picture
        self.profile_picture = profile_picture

    def serialize(self):
        return{
            "user_id":self.user_id,
            "username":self.username,
            "password":self.password,
            "profile_picture":self.profile_picture
        }


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    reciever_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
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

