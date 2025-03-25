import logging
from werkzeug.exceptions import InternalServerError, HTTPException, BadRequest
from .enums import CustomStatusCode

from .constants import *
from .helpers import *

# Initialize the logger
logger = logging.getLogger()

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        logger.exception(str(e), exc_info=e)
        response = create_response(CustomStatusCode.FAILURE.value, INTERNAL_SERVER_ERROR_MESSAGE)
        response.status_code = 500
        return response
    
    @app.errorhandler(InternalServerError)
    def handle_unexpected_http_error(e):
        logger.exception(str(e), exc_info=e)
        response = create_response(CustomStatusCode.FAILURE.value, INTERNAL_SERVER_ERROR_MESSAGE)
        response.status_code = InternalServerError.code
        return response

    @app.errorhandler(BadRequest)
    def handle_bad_request_exception(e):
        response = create_response(CustomStatusCode.BAD_REQUEST.value, e.description)
        response.status_code = e.code
        return response

    @app.errorhandler(HTTPException)
    def handle_exception(e):
        response = create_response(CustomStatusCode.FAILURE.value, e.description)
        response.status_code = e.code
        return response

#Error handler for user input validator
def url_validation_error_handler(err):
    error_message = str(err)
    return {
        "status": CustomStatusCode.BAD_REQUEST.value,
        "message": error_message
    }, 400