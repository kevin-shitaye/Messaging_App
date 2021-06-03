import os
import pathlib
import requests
from flask import Flask, jsonify, request, abort, session, redirect
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
from google_auth_oauthlib.flow import Flow
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

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "636882182686-ble33a9v9s7i94pauspdbs5hg4s4dgvl.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secrets_file.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


# arguments that need to be passed for Message
message_args = reqparse.RequestParser()
message_args.add_argument("content", type=str, help="This is the content")
# arguments that need to be passed for User
user_args = reqparse.RequestParser()
user_args.add_argument("username", type=str, help="This is the username")
user_args.add_argument("password", type=str, help="This is the password")
user_args.add_argument("picture",type=werkzeug.datastructures.FileStorage, help="This is the profile picture",location='files')



# documentation
@app.route('/')
def index():
    return render_template("documentation.html")


#athentication
#########################################################################################################
#decorator
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if id_token.verify_oauth2_token(token, google.auth.transport.requests.Request(session)):
            return function()
        else:
            return abort(401)  # Authorization required        
    return wrapper

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    print("hello")
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("http://127.0.0.1:3000/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("http://127.0.0.1:3000/")
#########################################################################################################

@app.route("/protected")
@login_is_required
def protected():
    return "protected"


class MessageSchema(Resource):
    
    def get(self, sender_username, reciever_username):
        messages = Message.query.filter(Message.sender_username==sender_username, Message.reciever_username==reciever_username)
        return jsonify([x.serialize() for x in messages]) 

    
    def post(self, sender_username, reciever_username):
        reciever = Users.query.filter(Users.username==reciever_username).first()
        sender = Users.query.filter(Users.username==reciever_username).first()
        if reciever and sender:
            args = message_args.parse_args()
            new_message = Message(sender_username=sender_username, reciever_username=reciever_username, content=args["content"])
            db.session.add(new_message)
            db.session.commit()
            return "message sent"
        return "Reviever does not exists" , 400


class UserSchema(Resource):
    def get(self, username):
        user = Users.query.filter(Users.username==username).first()
        if user == None:
            return "User does not exist", 400
        return jsonify(user.serialize()) 

    def post(self, username): #username is not used for post
        args = user_args.parse_args()
        user = Users.query.filter(Users.username==args["username"]).first()
        if user == None:
            new_user = Users(args["username"], args["password"])
            db.session.add(new_user)
            db.session.commit()
            return "User created"
        return "User already exists.", 400
    def put(self, username):
        args = user_args.parse_args()
        user = Users.query.filter(Users.username==username).first()
        username_taken = Users.query.filter(Users.username==args["username"]).first()
        #upload an image
        if request.files['picture']:
            file = request.files['picture']
            file.save("./static/" + file.filename)
            user.profile_picture = "/static/" + username + file.filename
        
        if args["username"]:
            if username_taken is None:
                user.username = args["username"]
                #reflect these change to the messages history of others
                messagesTo = Message.query.filter((Message.sender_username==username))
                messagesFrom = Message.query.filter((Message.reciever_username==username))
                for message in messagesTo:
                    message.sender_username = args["username"]
                    db.session.add(message)
                for message in messagesFrom:
                    message.reciever_username =args["username"]
                    db.session.add(message)
            else:  
                return "username taken", 400
        db.session.add(user)
        db.session.commit()
        return "Updated"
        

class ChattedWithSchema(Resource):
    def get(self, username):
        messagesTo = Message.query.filter((Message.sender_username==username))
        messagesFrom = Message.query.filter((Message.reciever_username==username))
        chatted_with = set() #a set to avoid repition
        for message in messagesTo:
            chatted_with.add(message.reciever_username)
        for message in messagesFrom:
            chatted_with.add(message.sender_username)

        return jsonify(list(chatted_with))



# API Endpoints
api.add_resource(MessageSchema, '/api/messages/<sender_username>/<reciever_username>')
api.add_resource(UserSchema, '/api/users/<username>')
api.add_resource(ChattedWithSchema, '/api/<username>/chatted_with')






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


