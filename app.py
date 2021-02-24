# import necessary libraries
import json
import pandas as pd
import pymysql
import pymongo
import sqlalchemy
from sqlalchemy import create_engine 
from flask import Flask, request, render_template, jsonify, make_response, session  
from flask_session import Session
from flask_cors import CORS 
import os 
from http import cookies
from uuid import uuid4
from rb_app_functions import get_session, get_cookie
from config import mongoConn, remote_db_endpoint, remote_db_port, remote_db_name, remote_db_user, remote_db_pwd

# instantiate Flask
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)
 
pymysql.install_as_MySQLdb() 
engine = create_engine(f"mysql://{remote_db_user}:{remote_db_pwd}@{remote_db_endpoint}:{remote_db_port}/{remote_db_name}")

index_model = {
    'user':{  'uid':'' },
    'ses':'',
    'log':'',
    'sid':''
} 

@app.route("/")
def home():  
    if 'uid' in request.cookies: 
        index_model['user']['uid'] = request.cookies['uid']   
    resp = make_response(render_template('index.html', index_model=index_model))
    return resp

@app.route("/test")
def test(): 
    index_model['user']['uid'] = ''
    if 'uid' in request.cookies: 
        index_model['user']['uid'] = request.cookies['uid']       
    if 'query_string' in session: 
        
        index_model['ses'] = f'ses: {session["query_string"]}'
        index_model['log']  =   f'query_string in session'
        index_model['sid']  = f'{session.sid}'
    else: 
        session['query_string'] = request.args.get('aaa')
        index_model['ses'] = session['query_string']
        index_model['log']  = f'query_string not in session '
        index_model['sid']  = f'{session.sid}'
    resp = make_response(render_template('index.html', index_model=index_model))    
    return resp
 
@app.route("/get_cookies")
def get_cookies(): 

    cookie='' 
    #resp.set_cookie('uid', '', expires=0) 
    if 'uid' not in request.cookies:   
        cookie=str(uuid4())
        index_model['user']['uid']=cookie
        resp = make_response(render_template('index.html', index_model=index_model))
        resp.set_cookie('uid', cookie ) 
    else:
        cookie = request.cookies['uid'] 
        index_model['user']['uid']=cookie
        resp = make_response(render_template('index.html', index_model=index_model)) 
 
    return resp

 
@app.route("/api/services")
def list_services():

    conn = engine.connect()
    sql = '''
        SELECT user_name, GROUP_CONCAT( ups.Service_Id ) sid
        FROM user_profile up
        LEFT JOIN user_profile_services ups ON up.User_Id = ups.User_Id 
        GROUP BY user_name
        LIMIT 10    
    '''
    df = pd.read_sql(sql, con=conn)
    _json = df.to_json(orient='records')
    conn.close()
    return jsonify(_json)


@app.route("/api/view/<view>")
def get_view(view): 
    conn = engine.connect() 
    sql = '''
    SELECT TABLE_NAME FROM (
        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS
        WHERE TABLE_SCHEMA = 'ripe_bananas' 
        UNION
        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'ripe_bananas' 
    ) DB_VIEWS_AND_TABLES  
    '''
    df = pd.read_sql(sql, con=conn)
    df=df.loc[df.TABLE_NAME == view]
    if len(df) < 1:
        return 'invalid db object'

    sql = f'''  SELECT * FROM {view} '''
    df = pd.read_sql(sql, con=conn)
    _json = df.to_json(orient='records')
    resp = make_response(_json)
    resp.headers['content-type'] = 'application/json' 
    conn.close()
    return resp



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
