
from flask import  request,  session 
import os 

def get_session(key, default=False):
    if key in session: 
        return session[key]
    else:
        return default 

def get_cookie(key,  default=False):
    if key in request.cookies: 
        return request.cookies[key]
    else:
        return default 