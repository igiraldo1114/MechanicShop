from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from . import mechanics_bp
from app.models import Mechanic, db
from .schemas import mechanic_schema, mechanics_schema, mechanic_login_schema, mechanic_activity_schema
from app.extensions import limiter, cache
from app.utils.auth import encode_mechanic_token, token_mechanic_required
from werkzeug.security import check_password_hash, generate_password_hash

# ========== SCHEMAS ==========


@mechanics_bp.route('/login', methods=['POST'])
def login():
    try:
        creds = mechanic_login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == creds['email'])
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic and check_password_hash(mechanic.password, creds['password']):
        token = encode_mechanic_token(mechanic.id)
        return jsonify({"token": token}), 200
    return jsonify({"message": "invalid email or password"}), 401

@mechanics_bp.route('/', methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    mechanic = db.session.execute(query).scalars().first()
    
    mechanic_data['password'] = generate_password_hash(mechanic_data['password'])
    
    if not mechanic:
        new_mechanic = Mechanic(**mechanic_data)
        db.session.add(new_mechanic)
        db.session.commit()
        return mechanic_schema.jsonify(new_mechanic), 201
    return jsonify({"message": "email already exists"}), 400
    


@mechanics_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_mechanics():
    try:
        query = select(Mechanic).options(db.joinedload(Mechanic.tickets))
        result = db.session.execute(query).unique().scalars().all()
        return mechanics_schema.jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@mechanics_bp.route('/<int:mechanic_id>', methods=['GET'])
@limiter.limit("20/day")
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    return jsonify({"message": "invalid mechanic id"}), 404
    

@mechanics_bp.route('/', methods=['PUT'])
@limiter.limit("5/day")
@token_mechanic_required
def update_mechanic():
    mechanic = db.session.get(Mechanic, request.mechanic_id)
    
    if not mechanic:
        return jsonify({"message": "invalid mechanic id"}), 404
    
    try:
        mechanic_data = mechanic_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == mechanic_data.get('email'))
    db_mechanic = db.session.execute(query).scalars().first()  
    
    if db_mechanic and db_mechanic.id != mechanic.id:
        return jsonify({"message": "email already exists"}), 400

    mechanic_data['password'] = generate_password_hash(mechanic_data['password'])
    for field, value in mechanic_data.items():
        setattr(mechanic, field, value)
    
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


@mechanics_bp.route('/', methods=['DELETE'])
@limiter.limit("8/day")
@token_mechanic_required
def delete_mechanic():
    mechanic = db.session.get(Mechanic, request.mechanic_id)
    
    if not mechanic:
        return jsonify({"message": "invalid mechanic id"}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": "mechanic deleted"}), 200



@mechanics_bp.route('/activity', methods=['GET'])
def mechanic_activity():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    
    mechanics_with_tickets = [mechanic for mechanic in mechanics if len(mechanic.tickets) > 0]
    
    if not mechanics_with_tickets:
        return jsonify({"message": "No active mechanics"}), 404
    
    mechanics_with_tickets.sort(key=lambda x: len(x.tickets), reverse=True)
    
    return jsonify({
        "mechanics": mechanic_activity_schema.dump(mechanics_with_tickets)
    }), 200
    
@mechanics_bp.route('/search', methods=['GET'])
def search_mechanic():
    name = request.args.get('search')
    
    query = select(Mechanic).where(Mechanic.name.ilike(f"%{name}%"))
    mechanics = db.session.execute(query).scalars().all()
    
    if not mechanics:
        return jsonify({"message": "No mechanics found matching the search"}), 404
    
    return jsonify({
        "mechanics": mechanics_schema.dump(mechanics)
    }), 200



