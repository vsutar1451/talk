from flask import Blueprint, render_template, request, redirect, session, jsonify, flash, url_for, abort
from flask import session
import hashlib
from flask_socketio import SocketIO,send
import json
from bson.json_util import dumps
from datetime import datetime, date
#custom imports
from app import *
from .models import *
import itertools
from twilio.rest import Client
import random
from bson.json_util import dumps
import math
from bson import ObjectId
from flask import make_response


chatapp = Blueprint("chatapp", __name__, template_folder='../template/chatapp_main', static_folder='../static',
                   static_url_path='../static')

users=mongo.db.users
chats=mongo.db.chats
@socketio.on('message')
def handlemessage(msg,username1,username2):
    print('message:'+msg)
    print(username1)
    print(username2)
    post = chats.find_one({"$or" : [ 
                                        { 
                                            "$and" :[
                                                {"username1":username1},
                                                {"username2":username2}
                                                ]
                                        },
                                        {
                                            "$and":[
                                                {"username1":username2},
                                                {"username2":username1}
                                                ]
                                        }
                                        ]
                                    } )
    
    if post != None:
        chat_room_id=post["_id"]
        chats.update_one({"_id": ObjectId(chat_room_id)}, {"$push": {"chats_core": {'username':session['username'],'msg':msg}}})
    else:
        chat_room_id=ObjectId()
        chats.insert({'_id':chat_room_id,'username1':username1,'username2':username2,'chats_core':[{'username':session['username'],'msg':msg}]})

    msg=msg
    
    send(msg)
    
    


@chatapp.errorhandler(404)
def page_not_found(error):
    return render_template('portal/404.html'), 404

@chatapp.route('/',methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone=""
        phone=request.form.get('phone')
        phone = "+91" + phone
        password = request.form.get('password')
        result = users.find_one( { "$and": [ { "phone": { "$eq": phone } }, { "password": { "$eq": password } } ] } )
        if result is not None:
            session['phone']=phone
            session['username']=result['name']
            session['chatname']=session['username']
            print("Welcome", session['username'])
            name = session['username']
            resp = make_response(render_template('chatapp_main.html'))
            resp.set_cookie('mycookie',session['username'])
        
            return resp
        else:
            return redirect("/chatapp/")
						  
                        
    return render_template("login.html")


@chatapp.route('/register1')
def register1():
    return render_template("register.html")


@chatapp.route('/register',methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.json['username']
        phone = request.json['phone']
        password = request.json['password']
        digits = [i for i in range(0, 10)]
        random_str = ""
        session['username']=username
        session['phone']=phone
        session['password']=password
        for i in range(6):
            index = math.floor(random.random() * 10)
            random_str += str(digits[index])

        
        print(random_str)
        account_sid ='AC8a48f482ebe5db42659a2cee1b879e64'
        auth_token = 'd93728a8865417e2f81c434e8c869983'
        client = Client(account_sid,auth_token)


        message = client.messages.create(
            body = random_str,
            from_ = '+12055256570',
            to=phone
        )
        print(message.sid)
        return jsonify(random_str)
    


@chatapp.route('/chatapp_main')
def chatapp_main():
    print("****************finally in here*****************")
    print("Welcome", session['username'])
    name=session['username']
    users.insert({'name': session['username'],'phone': session['phone'],'password':session['password']})
    response = render_template("chatapp_main.html",name=name)
    print(response)
    return response

'''
@chatapp.route('/dummy')
def dummy():
    name = session['username']
    response = render_template("dummy.html",name=name)
    print(response)
    return response'''

@chatapp.route('/dummy')
def dummy():
    name = session['username']
    response = render_template("dummy.html",name=name)
    print(response)
    return response
    

@chatapp.route('/get_session_name',methods = ['GET', 'POST'])
def get_session_name():
    username=session['chatname']

    print(username)
    print("got username")
    return dumps(username)

@chatapp.route('getchats',methods=['GET', 'POST'])
def getchats():
    print("IN get chats")
    data_received = request.get_data()
    data_received = data_received.decode("utf-8")
    data_received = json.loads(data_received)
    username1 = data_received['username1']
    username2 = data_received['username2']
    print(username1)
    print(username2)
    documents = chats.find_one({"$or" : [ 
                                        { 
                                            "$and" :[
                                                {"username1":username1},
                                                {"username2":username2}
                                                ]
                                        },
                                        {
                                            "$and":[
                                                {"username1":username2},
                                                {"username2":username1}
                                                ]
                                        }
                                        ]
                                    } )

    
    response=documents["chats_core"]
    return json.dumps(response)

@chatapp.route('getcontacts',methods=['GET', 'POST'])
def getcontacts():
    print("IN get contacts")
    documents = users.find()
    print(documents)
    response = []
    for document in documents:
        document['_id'] = str(document['_id'])
        response.append(document)
    print(response)
    return json.dumps(response)

@chatapp.route('/fetch_search_data', methods=['GET', 'POST'])
def fetch_search_data():
    try:
        print("*******************************IN HERE ******************************************************")
        data_received = request.get_data()
        data_received = data_received.decode("utf-8")
        data_received = json.loads(data_received)
        abc = data_received['text']
        abc=str(abc)
        print(abc)
        print(abc[0])
        for i in range(len(abc)) : 
            if abc[i].isdigit() != True : 
                print("")
            else:
                abc="+91"+abc
        username = session['username']
        username=str(username)
        
        print(username)
        posts = users.find({"$text": {"$search": abc} })
        response=[]
        for document in posts:
            document['_id'] = str(document['_id'])
            response.append(document)
        print(response)
        return json.dumps(response)
    except Exception as error:
        print(' In the views exception: ',error)
        return []

chatapp.route('/isNumber/<s>')
def isNumber(s) : 
    print("in isnumber")
    print(len(s))
    for i in range(len(s)) : 
        if s[i].isdigit() != True : 
            return False
  
    return True