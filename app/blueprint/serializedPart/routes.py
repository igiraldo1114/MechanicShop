from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from . import serializedparts_bp
from .schemas import serialized_part_schema, serialized_parts_schema
from app.models import SerializedPart, db
from app.extensions import limiter, cache
    

    
# ========== SCHEMAS ==========


# ================crud==================
    
@serializedparts_bp.route('/paginate', methods=['GET'])
def page_parts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 3, type=int)
    
    query = select(SerializedPart)
    parts = db.session.execute(query).scalars().all()
    
    total_parts = len(parts)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_parts = parts[start:end]
    
    return jsonify({
        'total_part': total_parts,
        'page': page,
        'per_page': per_page,
        'parts': serialized_parts_schema.dump(paginated_parts)
    }), 200



@serializedparts_bp.route('/', methods=['POST'])
@limiter.limit("15/hour")
def create_part():
    try:
        part_data = serialized_part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_part = SerializedPart(**part_data)
    
    db.session.add(new_part)
    db.session.commit()
    return jsonify({
        "message": f"{new_part.description.brand} {new_part.description.part_name} added successfully",
        "part": serialized_part_schema.dump(new_part)
        
        }), 201


@serializedparts_bp.route('/', methods=['GET'])
@limiter.exempt
@cache.cached(timeout=60)
def get_parts():
    try:
        query = select(SerializedPart)
        result = db.session.execute(query).scalars().all()
        return serialized_parts_schema.jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  
    

@serializedparts_bp.route('/<int:part_id>', methods=['PUT'])
@limiter.limit("5/hour")
def update_part(serialized_part_id):
    query = select(SerializedPart).where(SerializedPart.id == serialized_part_id)
    part = db.session.execute(query).scalars().first()
    
    if part == None:
        return jsonify({"message: inavlid part id"}), 404
    
    try:
        part_data = serialized_part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in part_data.items():
        setattr(part, field, value)
        
    db.session.commit()
    return serialized_part_schema.jsonify(part), 200

@serializedparts_bp.route('/', methods=['DELETE'])
@limiter.limit("5/hour")
def delete_part(serialized_part_id):
    try:
        part = db.session.get(SerializedPart, serialized_part_id)
        
        if part:
            db.session.delete(part)
            db.session.commit()
            return jsonify({"message": "part deleted successfully"}), 200
        
        return jsonify({"message": "part not found"}), 404
    except Exception as e:
        return jsonify({"error": "An error occurred while deleting the part", "details": str(e)}), 500
    
    
    
# @serializedparts_bp.route('/search', methods=['GET'])
# def search_customers():
#     email = request.args.get('search')
    
#     query = select(Customer).where(Customer.email.ilike(f"%{email}%"))
#     customer = db.session.execute(query).scalars().all()
    
#     if not customer:
#         return jsonify({"message": "No customers found matching the search"}), 404
    
#     return jsonify({
#         "mechanics": customers_schema.dump(customer)
#     }), 200
    
