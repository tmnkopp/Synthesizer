# import necessary libraries
import json
import pandas as pd
import pymysql
import pymongo
import sqlalchemy
from sqlalchemy import create_engine 
from flask import Flask, request, render_template, jsonify, make_response, session 
import os 
from http import cookies
from uuid import uuid4

# Heroku check
is_heroku = False
if 'IS_HEROKU' in os.environ:
    is_heroku = True

# instantiate Flask
app = Flask(__name__)

if is_heroku == True:
    # if IS_HEROKU is found in the environment variables, then use the rest
    # NOTE: you still need to set up the IS_HEROKU environment variable on Heroku (it is not there by default)
    mongoConn = os.environ.get('mongoConn')
    remote_db_endpoint = os.environ.get('remote_db_endpoint')
    remote_db_port = os.environ.get('remote_db_port')
    remote_db_name = os.environ.get('remote_db_name')
    remote_db_user = os.environ.get('remote_db_user')
    remote_db_pwd = os.environ.get('remote_db_pwd')
else:
    # use the config.py file if IS_HEROKU is not detected
    from config import mongoConn, remote_db_endpoint, remote_db_port, remote_db_name, remote_db_user, remote_db_pwd

pymysql.install_as_MySQLdb() 
engine = create_engine(f"mysql://{remote_db_user}:{remote_db_pwd}@{remote_db_endpoint}:{remote_db_port}/{remote_db_name}")

@app.route("/")
def home():  
    user= ''
    if user in session:
        user = session['sesuser']
    return user
 
@app.route("/get_cookies")
def get_cookies():  
    cookie='' 
    #resp.set_cookie('uid', '', expires=0) 
    if 'uid' not in request.cookies:  
        #resp.set_cookie('user', str(uuid4())) 
        cookie=str(uuid4())
        resp = make_response(render_template('index.html', cook=cookie))
        resp.set_cookie('uid', cookie)
        
    else:
        cookie = request.cookies['uid'] 
        resp = make_response(render_template('index.html', cook=cookie)) 
    # d={ 'session': session['sesuser'], 'cookie': cookie  } 
    return resp

@app.route("/set_cookies/<string:cookie>")
def set_cookies(cookie):   
    resp = make_response(render_template('index.html', cookie=cookie))
    resp.set_cookie('user', cookie) 
    cookie = request.cookies['user']
    session['user'] = cookie
    return resp 
 
@app.route("/api/services")
def list_services():

    conn = engine.connect()
    sql = '''
    SELECT user_name, GROUP_CONCAT( ups.Service_Id ) sid
    FROM user_profile up
    LEFT JOIN user_profile_services ups ON up.User_Id = ups.User_Id 
    GROUP BY user_name
    LIMIT 10    '''
    df = pd.read_sql(sql, con=conn)
    _json = df.to_json(orient='records')
    conn.close()
    return jsonify(_json)

@app.route("/api/lookup")
def mongodata():
    client = pymongo.MongoClient(mongoConn) 
    db = client.shows_db
    collection = db.items
    results = collection.find({}, {'_id': False})
    coll_df = pd.DataFrame(results)
    coll_json = coll_df.to_json(orient='records')
    return coll_json
# run the app in debug mode
if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True)
