from app.constants import SUCCESS_MESSAGE, INVALID_CREDENTIALS
from app.enums.custom_status_code import CustomStatusCode
from app.error_handler import url_validation_error_handler
from app.helpers import create_response, get_record_by_field, add_record_to_database, generate_jwt_token, token_required
from app.models import User, UserSession
from flask_parameter_validation import ValidateParameters, Json
from . import routes_blueprint
from ..extensions.database import session
import bcrypt

@routes_blueprint.route("/api/auth/google", methods=["POST"])
@ValidateParameters(url_validation_error_handler)
def google_login(name: str = Json(), email: str = Json(), google_id: str = Json()):
    try:
        user = get_record_by_field(User, "email", email)

        if not user:
            user = User(fullname=name, email=email, google_id=google_id)
            add_record_to_database(user)

        token = generate_jwt_token(user)
        session = UserSession(user_id=user.id, token=token)
        add_record_to_database(session)

        serialized_user = user.serialize()

        return create_response(CustomStatusCode.SUCCESS.value, SUCCESS_MESSAGE, {"id": user.id, "token":token,
                                                                                 "email": email, "name": name, "notebooks":serialized_user["notebooks"]}), 200

    except ValueError:
        return create_response(CustomStatusCode.BAD_REQUEST.value, "Invalid Token"), 400

@routes_blueprint.route('/logout', methods=['POST'])
@token_required
def logout(user_id):
    UserSession.query.filter_by(user_id=user_id).delete()
    session.commit()
    return create_response(CustomStatusCode.SUCCESS.value, "Logged out successfully!"), 200

@routes_blueprint.route('/ping', methods=['GET'])
def ping():
    return create_response(CustomStatusCode.SUCCESS.value, "API is Awake"), 200

@routes_blueprint.route("/api/login", methods=["POST"])
@ValidateParameters(url_validation_error_handler)
def login(email: str = Json(), password: str = Json()):
    try:
        user = get_record_by_field(User, "email", email)

        if not user:
            return create_response(CustomStatusCode.FAILURE.value, "Invalid Credentials", {}), 400

        if(bcrypt.checkpw(password.encode('utf-8'), password)):
            token = generate_jwt_token(user)
            session = UserSession(user_id=user.id, token=token)
            add_record_to_database(session)

            serialized_user = user.serialize()

            return create_response(CustomStatusCode.SUCCESS.value, SUCCESS_MESSAGE, {"id": user.id, "token": token,
                                                                                     "email": email, "name": user.name, "notebooks":serialized_user["notebooks"]}), 200

        return create_response(CustomStatusCode.FAILURE.value, INVALID_CREDENTIALS, {}), 400

    except ValueError:
        return create_response(CustomStatusCode.BAD_REQUEST.value, "Error Occured"), 400

@routes_blueprint.route("/api/register", methods=["POST"])
@ValidateParameters(url_validation_error_handler)
def register(name: str = Json(), email: str = Json(), password: str = Json()):
    try:
        user = get_record_by_field(User, "email", email)

        if user:
            return create_response(CustomStatusCode.FAILURE.value, "User Already Exists", {}), 400

        salt = bcrypt.gensalt()
        hash_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        user = User(fullname=name, email=email, password=hash_password)
        add_record_to_database(user)

        return create_response(CustomStatusCode.SUCCESS.value, SUCCESS_MESSAGE, {}), 200
    except ValueError:
        return create_response(CustomStatusCode.BAD_REQUEST.value, "Invalid Token"), 400
