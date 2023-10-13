

import os
from functools import wraps

import config
import jwt
from flask import jsonify, request, current_app

def create_token(payload):
    return jwt.encode(payload, config.JWT_KEY, algorithm='HS256')

def token_valid(t):
    #current_app.logger.info("************** %s",t)
    try:
        data = jwt.decode(t, key=config.JWT_KEY, algorithms=['HS256'])
        return True
    except:
        return False

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if os.getenv("DEBUG",False):
            return f(*args, **kwargs)
        
        token = request.cookies.get('token', None)

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, key=config.JWT_KEY, algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)

    return decorated
