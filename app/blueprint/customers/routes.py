from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from . import customers_bp
from .schemas import customer_schema, customers_schema
from app.models import Customer, db
    

    
# ========== SCHEMAS ==========


# ================crud==================

@customers_bp.route('/', methods=['POST'])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_customer = Customer(name=customer_data['name'], phone=customer_data['phone'], email=customer_data['email'])
    
    db.session.add(new_customer)    
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201


@customers_bp.route('/', methods=['GET'])
def get_customers():
    try:
        query = select(Customer)
        result = db.session.execute(query).scalars().all()
        return customers_schema.jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  
    

@customers_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    
    if customer == None:
        return jsonify({"message: inavlid customer id"}), 404
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in customer_data.items():
        setattr(customer, field, value)
        
    db.session.commit()
    return customer_schema.jsonify(customer), 200

@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer = db.session.get(Customer, customer_id)
        
        if customer:
            db.session.delete(customer)
            db.session.commit()
            return jsonify({"message": "Customer deleted successfully"}), 200
        
        return jsonify({"message": "Customer not found"}), 404
    except Exception as e:
        return jsonify({"error": "An error occurred while deleting the customer", "details": str(e)}), 500