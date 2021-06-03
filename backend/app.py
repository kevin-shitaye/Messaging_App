import os
import pathlib
import requests
from flask import Flask, jsonify, request, abort, session
from flask.helpers import url_for
from flask.templating import render_template
from flask_restful import Api, Resource, reqparse
# from flask_socketio import SocketIO, emit
from flask_cors import CORS
# import asyncio
from models import Users, Message, db
from settings import *
import werkzeug
from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests





app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS


CORS(app, supports_credentials=True)
# socketio = SocketIO(app, cors_allowed_origins="*")
# main_event_loop = asyncio.get_event_loop()

api = Api(app)
db.init_app(app)

# os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# GOOGLE_CLIENT_ID = "636882182686-ble33a9v9s7i94pauspdbs5hg4s4dgvl.apps.googleusercontent.com"
# client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secrets_file.json")

# flow = Flow.from_client_secrets_file(
#     client_secrets_file=client_secrets_file,
#     scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
#     redirect_uri="http://127.0.0.1:5000/callback"
# )



# arguments that need to be passed for Message
message_args = reqparse.RequestParser()
message_args.add_argument("content", type=str, help="This is the content")
# arguments that need to be passed for User
user_args = reqparse.RequestParser()
user_args.add_argument("username", type=str, help="This is the username")
user_args.add_argument("picture", type=werkzeug.datastructures.FileStorage, help="This is the profile picture",location='files')


# documentation
@app.route('/')
def index():
    return render_template("documentation.html")


class RegisterUser(Resource):
    def get(self, token):
        google_id_info = id_token.verify_oauth2_token(token, google.auth.transport.requests.Request(session))
        if google_id_info:
            user = Users.query.filter(Users.user_id==google_id_info['sub']).first()
            if user == None:
                # adding to database
                new_user = Users(user_id=google_id_info["sub"] ,username=google_id_info["given_name"], profile_picture=google_id_info["picture"])
                db.session.add(new_user)
                db.session.commit()
                return "User added to Database.", 201
            return "User already in database.", 200
            
        return "Token verification failed", 401



class MessageSchema(Resource):


    def get(self, reciever_id):
        google_id_info = id_token.verify_oauth2_token(request.headers["tokenId"], google.auth.transport.requests.Request(session))
        if google_id_info:
            messagesto = Message.query.filter(Message.sender_id==google_id_info['sub'], Message.reciever_id==reciever_id).all()
            messagesfrom = Message.query.filter(Message.sender_id==reciever_id, Message.reciever_id==google_id_info['sub']).all()
            messages = messagesto + messagesfrom
            messages = set(messages) 
            return jsonify([x.serialize() for x in messages]) 
        return "UNATHOTIZED", 401

    def post(self, reciever_id):
        args = user_args.parse_args()
        google_id_info = id_token.verify_oauth2_token(request.headers["tokenId"], google.auth.transport.requests.Request(session))
        if google_id_info:
            reciever = Users.query.filter(Users.user_id==reciever_id).first()
            sender = Users.query.filter(Users.user_id==google_id_info['sub']).first()
            if reciever and sender:
                args = message_args.parse_args()
                new_message = Message(sender_id=google_id_info['sub'], reciever_id=reciever_id, content=args["content"])
                db.session.add(new_message)
                db.session.commit()
                return "message sent"
            return "User does not exists" , 400
        return "UNATHOTIZED", 401

class UserSchema(Resource):
    def get(self, user_id):
        user = Users.query.filter(Users.user_id==user_id).first()
        if user == None:
            return "User does not exist", 400
        return jsonify(user.serialize()) 

    def put(self, user_id):
        args = user_args.parse_args()
        google_id_info = id_token.verify_oauth2_token(request.headers["tokenId"], google.auth.transport.requests.Request(session))
        if google_id_info:
            if user_id == google_id_info['sub']:
                
                user = Users.query.filter(Users.user_id==user_id).first()
                print(2)
                # upload an image
                if args['picture']:
                    file = request.files['picture']
                    file.save("./static/" + file.filename)
                    user.profile_picture = "/static/" + user_id + file.filename
                print(2)
                #change username
                if args["username"]:
                    print(3)
                    user.username = args["username"]
                db.session.add(user)
                db.session.commit()
                return "Updated"
            return "UNATHOTIZED Request: Can't update inforamtion of another user", 401
        return "UNATHOTIZED", 401

class ChattedWithSchema(Resource):
    def get(self):
 
        google_id_info = id_token.verify_oauth2_token(request.headers["tokenId"], google.auth.transport.requests.Request(session))
        if google_id_info:
            messagesTo = Message.query.filter((Message.sender_id==google_id_info['sub'])).all()
            messagesFrom = Message.query.filter((Message.reciever_id==google_id_info['sub'])).all()
            chatted_with = set() #a set to avoid repition
            for message in messagesTo:
                if(message.reciever_id):
                    chatted_with.add(message.reciever_id)
                
            for message in messagesFrom:
                if(message.sender_id):
                    chatted_with.add(message.sender_id)

            return jsonify(list(chatted_with))



# API Endpoints
api.add_resource(RegisterUser, "/api/authorize/<token>")
api.add_resource(MessageSchema, '/api/messages/<reciever_id>')
api.add_resource(UserSchema, '/api/users/<user_id>')
api.add_resource(ChattedWithSchema, '/api/chatted_with')






# @socketio.on('message')
# def handleMessage(msg):
#     print(msg)
#     main_event_loop.run_until_complete(socketio.emit("announce message", msg, broadcast=True))
    

# @socketio.on('message2')
# def handleMessage2(msg):
#     print(msg)
#     main_event_loop.run_until_complete(socketio.emit("announce message2", msg, broadcast=True))



if __name__ == "__main__":
    app.run(debug=True)
    # socketio.run(app, debug=True)


