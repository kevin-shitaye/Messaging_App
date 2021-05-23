from flask import Flask, jsonify
from flask_restful import Api, Resource
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import asyncio



app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
main_event_loop = asyncio.get_event_loop()

api = Api(app)

products = [
    {
        "id":1,
        "p_name":"item1"
    },
            {
        "id":2,
        "p_name":"item2"
    },
            {
        "id":3,
        "p_name":"item3"
    }
]

# @app.route('/api')
# def index():
#     return jsonify(products)


@socketio.on('message')
def handleMessage(msg):
    print(msg)
    main_event_loop.run_until_complete(socketio.emit("announce message", msg, broadcast=True))
    

@socketio.on('message2')
def handleMessage2(msg):
    print(msg)
    main_event_loop.run_until_complete(socketio.emit("announce message2", msg, broadcast=True))



class Products(Resource):
    def get(self):
        return jsonify(products)

api.add_resource(Products, '/api/products/')



if __name__ == "__main__":
    app.run(debug=True)
    socketio.run(app, debug=True)


