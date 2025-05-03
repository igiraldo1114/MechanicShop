from flask import Blueprint

serializedparts_bp = Blueprint('serializedparts_bp', __name__)

from . import routes
