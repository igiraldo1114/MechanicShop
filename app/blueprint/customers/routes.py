from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.utils.auth import encode_token, token_required
from . import customers_bp
from .schemas import customer_schema, customers_schema, login_schema
from app.models import Customer, ServiceTicket, db
from app.extensions import limiter, cache
from werkzeug.security import check_password_hash, generate_password_hash
    

    
# ========== SCHEMAS ==========


# ================crud==================
    

@customers_bp.route('/login', methods=['POST'])
def login():
    try:
        creds = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == creds['email'])
    customer = db.session.execute(query).scalars().first()
    
    if customer and check_password_hash(customer.password, creds['password']):
        token = encode_token(customer.id)
        return jsonify({"token": token}), 200
    return jsonify({"message": "invalid email or password"}), 401


@customers_bp.route('/', methods=['POST'])
@limiter.limit("15/hour")
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    customer = db.session.execute(query).scalars().first()
    customer_data['password'] = generate_password_hash(customer_data['password'])
    if not customer:
        new_customer = Customer(**customer_data)   
        db.session.add(new_customer)
        db.session.commit()
        return customer_schema.jsonify(new_customer), 201
    return jsonify({"message": "customer already exists"}), 400


@customers_bp.route('/paginate', methods=['GET'])
@cache.cached(timeout=60)
@limiter.exempt
def page_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 3, type=int)
    
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()
    
    total_customers = len(customers)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_customers = customers[start:end]
    
    return jsonify({
        'total_customers': total_customers,
        'page': page,
        'per_page': per_page,
        'customers': customers_schema.dump(paginated_customers)
    }), 200
    
    
@customers_bp.route('/<int:customer_id>', methods=['GET'])
@limiter.limit("20/day")
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"message": "invalid customer id"}), 404



@customers_bp.route('/', methods=['PUT'])
@limiter.limit("5/day")
@token_required
def update_customer():
    customer = db.session.get(Customer, request.customer_id) 
    try:
        customer_data = customer_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == customer_data.get('email'))
    db_customer = db.session.execute(query).scalars().first()
    
    if db_customer and db_customer.id != customer.id:
        return jsonify({"message": "Email already exists"}), 400

    if 'password' in customer_data:
        customer_data['password'] = generate_password_hash(customer_data['password'])
    
    for field, value in customer_data.items():
        setattr(customer, field, value)
    
    db.session.commit()
    return customer_schema.jsonify(customer), 200

@customers_bp.route('/', methods=['DELETE'])
@limiter.limit("5/hour")
@token_required
def delete_customer():
    customer = db.session.get(Customer, request.customer_id) 
    
    if not customer:
        return jsonify({"message": "Customer not found"}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted successfully"}), 200
    
    

@customers_bp.route('/my-tickets', methods=['GET'])
@token_required
def my_tickets():
    customer = db.session.get(Customer, request.customer_id)

    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    tickets = db.session.query(ServiceTicket).filter_by(customer_id=customer.id).all()

    if not tickets:
        return jsonify({"message": "No tickets found"}), 404

    return jsonify({
        "tickets": [ticket.service_desc for ticket in tickets]
    }), 200
    
@customers_bp.route('/search', methods=['GET'])
def search_customers():
    email = request.args.get('search')
    
    query = select(Customer).where(Customer.email.ilike(f"%{email}%"))
    customer = db.session.execute(query).scalars().all()
    
    if not customer:
        return jsonify({"message": "No customers found matching the search"}), 404
    
    return jsonify({
        "customers": customers_schema.dump(customer)
    }), 200
    
