from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
# from app.utils.auth import encode_token, token_required
from . import inventory_bp
from .schemas import inventory_schema, inventorys_schema
from app.models import Inventory, db
from app.extensions import limiter, cache
    

    
# ========== SCHEMAS ==========


# ================crud==================
    
    
@inventory_bp.route('/paginate', methods=['GET'])
def page_inventory():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 3, type=int)
    
    query = select(Inventory)
    descriptions = db.session.execute(query).scalars().all()
    
    total_descriptions = len(descriptions)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_descriptions = descriptions[start:end]
    
    return jsonify({
        'total_customers': total_descriptions,
        'page': page,
        'per_page': per_page,
        'customers': inventorys_schema.dump(paginated_descriptions)
    }), 200


@inventory_bp.route('/', methods=['POST'])
@limiter.limit("15/hour")
def create_part():
    try:
        description_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_description = Inventory(**description_data)
    
    db.session.add(new_description)
    db.session.commit()
    return inventory_schema.jsonify(new_description), 201


@inventory_bp.route('/', methods=['GET'])
@limiter.exempt
@cache.cached(timeout=60)
def get_part_descriptions():
    try:
        query = select(Inventory)
        result = db.session.execute(query).scalars().all()
        return inventorys_schema.jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  
    

    
@inventory_bp.route('/<int:inventory_id>', methods=['GET'])
@cache.cached(timeout=60)
@limiter.limit("20/day")
def get_inventory(inventory_id):
    description = db.session.get(Inventory, inventory_id)
    
    if description:
        return inventory_schema.jsonify(description), 200
    return jsonify({"message": "invalid id"}), 404
    

@inventory_bp.route('/<int:inventory_id>', methods=['PUT'])
@limiter.limit("5/hour")
def update_description(inventory_id):
    query = select(Inventory).where(Inventory.id == inventory_id)
    description = db.session.execute(query).scalars().first()
    
    if description == None:
        return jsonify({"message: inavlid id"}), 404
    
    try:
        description_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in description_data.items():
        setattr(description, field, value)
        
    db.session.commit()
    return inventory_schema.jsonify(description), 200

@inventory_bp.route('/<int:inventory_id>', methods=['DELETE'])
@limiter.limit("5/hour")
def delete_inventory_item(inventory_id):
    description = db.session.get(Inventory, inventory_id)
        
    if not description:
        return jsonify({"message": "invalid id"}), 404
        
    db.session.delete(description)
    db.session.commit()
    return jsonify({"message": "description deleted successfully"}), 200



    
