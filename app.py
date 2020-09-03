from flask import Flask,request,render_template
from flask_pymongo import PyMongo
from flask_socketio import SocketIO,send
from pymongo import MongoClient
# from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object("config.Config")
socketio=SocketIO(app)

# csrf = CSRFProtect(app)

app.config['MONGO_DBNAME'] = 'new_database'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/new_database'
mongo = PyMongo(app)

from chatapp.views import chatapp



app.register_blueprint(chatapp, url_prefix='/chatapp')



if __name__ == '__main__':
    app.run(Debug=True)
    
    

