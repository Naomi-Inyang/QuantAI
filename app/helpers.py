from .extensions.database import database, session
from .models import UserSession
from flask import abort, jsonify, request
from functools import wraps
import jwt
import datetime
from .constants import APP_SECRET_KEY
import secrets

def is_valid_number(value):
    # Check if the value is a number
    return isinstance(value, (int, float))


def add_record_to_database(record):
    try:
        session.add(record)
        session.commit()
    except Exception as e:
        print(e)
        database.session.rollback()

def add_records_to_database(records):
    try:
        session.add_all(records)
        session.commit()
    except Exception as e:
        session.rollback()

def get_record_by_field(model, field, value):
    try:
        return session.query(model).filter(getattr(model, field) == value).first()
    except Exception as e:
        print(f"Error fetching record: {e}")
        return None
    
def create_response(status: bool, message: str, data=None):
    response = {
        "status": status,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response)


def generate_jwt_token(user):
    token = secrets.token_hex(16)
    # payload = {
    #     "user_id": user.id,
    #     "name": user.fullname,
    #     "email": user.email,
    #     "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
    #     "iat": datetime.datetime.utcnow(),
    # }
    #
    # token = jwt.encode(payload, APP_SECRET_KEY, algorithm="HS256")
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            token = token.split(" ")[1]  # Remove "Bearer" prefix
            data = jwt.decode(token, APP_SECRET_KEY, algorithms=["HS256"])
            user_id = data["user_id"]

            # Check token in DB
            session = UserSession.query.filter_by(user_id=user_id, token=token).first()
            if not session or session.expires_at < datetime.utcnow():
                return jsonify({"message": "Invalid or expired token!"}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401

        return f(user_id, *args, **kwargs)

    return decorated
