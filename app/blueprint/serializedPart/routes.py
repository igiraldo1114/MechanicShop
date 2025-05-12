from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from . import serializedparts_bp
from .schemas import serialized_part_schema, serialized_parts_schema
from app.models import SerializedPart, db, Inventory
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

    desc_id = part_data.get('desc_id')
    inventory_part = db.session.get(Inventory, desc_id)
    if not inventory_part:
        return jsonify({"message": "Invalid desc_id. No matching inventory part found."}), 400

    new_part = SerializedPart(**part_data)
    db.session.add(new_part)
    db.session.commit()
    return jsonify({
        "message": f"{inventory_part.brand} {inventory_part.part_name} added successfully",
        "part": serialized_part_schema.dump(new_part)
    }), 201
    
    

@serializedparts_bp.route('/<int:serialized_part_id>', methods=['DELETE'])
@limiter.limit("5/hour")
def delete_part(serialized_part_id):
    try:
        part = db.session.get(SerializedPart, serialized_part_id)
        
        if part:
            db.session.delete(part)
            db.session.commit()
            return jsonify({"message": "successfully deleted serialized part."}), 200
        
        return jsonify({"message": "part not found"}), 404
    except Exception as e:
        return jsonify({"error": "An error occurred while deleting the part", "details": str(e)}), 500
    
@serializedparts_bp.route('/stock/<int:description_id>', methods=['GET'])
@limiter.exempt
def get_stock(description_id):
    inventory_part = db.session.get(Inventory, description_id)
    
    if not inventory_part:
        return jsonify({"message": "Inventory part not found"}), 404

    query = select(SerializedPart).join(Inventory).where(Inventory.part_name == inventory_part.part_name)
    parts = db.session.execute(query).scalars().all()
    count = len(parts)  

    return jsonify({
        "Item": inventory_part.part_name, 
        "stock": count  
    }), 200


    

    
