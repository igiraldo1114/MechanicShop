from flask import Flask
from app.extensions import ma, limiter, cache
from app.models import db
from app.blueprint.customers import customers_bp
from app.blueprint.mechanics import mechanics_bp
from app.blueprint.service_tickets import service_tickets_bp
from app.blueprint.serializedPart import serializedparts_bp
from app.blueprint.Inventory import inventory_bp

def create_app(config_name):
    
    
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')
    
    
    ma.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    
    # register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(service_tickets_bp, url_prefix='/service-ticket')
    app.register_blueprint(serializedparts_bp, url_prefix='/serialized-part')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    
    
    return app