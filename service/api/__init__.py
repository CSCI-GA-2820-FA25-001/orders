"""
Flask-RESTX API initialization
"""
from flask_restx import Api
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

api = Api(
    api_bp,
    version='1.0',
    title='Orders REST API',
    description='A simple Orders service API with Swagger documentation',
    doc='/apidocs/',
    default='Orders',
    default_label='Orders operations'
)

from . import orders, orderitems

api.add_namespace(orders.ns)
api.add_namespace(orderitems.ns)
