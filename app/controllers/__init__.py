from flask import Blueprint

routes_blueprint = Blueprint(
    'routes', __name__
)

from . import auth
from . import notebook
from . import dashboard