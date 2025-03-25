from app.constants import SUCCESS_MESSAGE
from app.enums.custom_status_code import CustomStatusCode
from app.error_handler import url_validation_error_handler
from app.helpers import create_response, token_required
from app.services import notebook
from app.repository import base
from app.models import Notebook
from flask_parameter_validation import ValidateParameters, Query, Route
from . import routes_blueprint

@routes_blueprint.route('/notes', methods=['GET'])
@ValidateParameters(url_validation_error_handler)
def get_note_from_query(user_id:int = Query(), query:str = Query()):
    data = notebook.get_note_from_query(user_id, query)
    return create_response(CustomStatusCode.SUCCESS.value, SUCCESS_MESSAGE, data), 200

@routes_blueprint.route('/notes/<int:id>', methods=['GET'])
@ValidateParameters(url_validation_error_handler)
def get_note(id:int = Route()):
    notebook = base.get_record_by_field(Notebook, "id", id)
    return create_response(CustomStatusCode.SUCCESS.value, SUCCESS_MESSAGE, notebook.serialize()), 200

@routes_blueprint.route('/users/<int:user_id>/notes', methods=['GET'])
@ValidateParameters(url_validation_error_handler)
def get_user_notes(user_id:int = Route()):
    notebooks = notebook.get_user_notebooks(user_id)
    return create_response(CustomStatusCode.SUCCESS.value, SUCCESS_MESSAGE, notebooks), 200

@routes_blueprint.route('/notes/<int:id>', methods=['DELETE'])
@ValidateParameters(url_validation_error_handler)
def delete_note(id:int = Route()):
    base.delete_records_by_field(Notebook, 'id', id)
    return create_response(CustomStatusCode.SUCCESS.value, SUCCESS_MESSAGE), 200