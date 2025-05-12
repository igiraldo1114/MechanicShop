from jose import jwt, exceptions
import jose
from datetime import datetime, timedelta, timezone
from flask import request, jsonify
from functools import wraps
import os


SECRET_KEY = os.environ.get('SECRET_KEY') or 'super secret secrets'

def encode_mechanic_token(mechanic_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=30, hours=0),
        'iat': datetime.now(timezone.utc),
        'sub': str(mechanic_id)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token




def token_mechanic_required(f):
    @wraps(f)
    def Mechanicdecorator(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
            
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.mechanic_id = int(data['sub'])
            
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
            return jsonify({'message': 'Invalid token!'}), 401
        
        return f(*args, **kwargs)
    return Mechanicdecorator


def encode_token(customer_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=15, hours=0),
        'iat': datetime.now(timezone.utc),
        'sub': str(customer_id)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.customer_id = int(data['sub'])

        except exceptions.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except exceptions.JWTError:
            return jsonify({"message": "Invalid token!"}), 401

        return f(*args, **kwargs)  

    return decorator