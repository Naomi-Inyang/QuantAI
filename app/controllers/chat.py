from . import routes_blueprint
from ..services import chat
from flask import request
from flask_parameter_validation import ValidateParameters, Json
from typing import Optional
from ..error_handler import url_validation_error_handler
from ..helpers import create_response
from ..constants import SUCCESS_MESSAGE
from ..enums import CustomStatusCode

@routes_blueprint.route('/start-chat', methods=['POST'])
@ValidateParameters(url_validation_error_handler)
def start_chat(stock:str = Json(), user_id: Optional[int] = Json()):
    response = chat.start_chat(request.get_json())
    return create_response(CustomStatusCode.SUCCESS.value, SUCCESS_MESSAGE, response), 200

@routes_blueprint.route('/prompt', methods=['POST'])
def continue_chat(query:str = Json(), chat_id: int = Json()):
    response = chat.continue_chat(request.get_json())
    return create_response(CustomStatusCode.SUCCESS.value, SUCCESS_MESSAGE, response), 200

