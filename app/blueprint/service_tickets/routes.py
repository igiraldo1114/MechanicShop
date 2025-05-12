from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import Mechanic, SerializedPart, ServiceTicket, Customer, db
from .schemas import service_ticket_schema, service_tickets_schema
from app.blueprint.mechanics.schemas import mechanics_schema
from . import service_tickets_bp
from app.extensions import limiter
from app.blueprint.serializedPart.schemas import responses_schema 


# create ticket 

@service_tickets_bp.route('/', methods=['POST'])
def create_ticket():
    try:
        ticket_data = service_ticket_schema.load(request.json, partial=("customer",))
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer_id = request.json.get('customer_id') 

    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"message": "Invalid customer ID"}), 400

    ticket_data['customer_id'] = customer_id
    new_ticket = ServiceTicket(**ticket_data)
    db.session.add(new_ticket)
    db.session.commit()

    return service_ticket_schema.jsonify(new_ticket), 201

# get tickets 
@service_tickets_bp.route('/', methods=['GET'])
@limiter.exempt
def get_tickets():
    query = select(ServiceTicket)
    tickets = db.session.execute(query).scalars().all()
    
    if tickets:
        return service_tickets_schema.jsonify(tickets), 200
    return jsonify({"message": "no tickets found"}), 404


# get a specific ticket
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['GET'])
@limiter.exempt
def get_ticket(service_ticket_id):
    ticket = db.session.get(ServiceTicket, service_ticket_id)
    
    if ticket:
        return service_ticket_schema.jsonify(ticket), 200
    return jsonify({"message": "no ticket found"}), 404


# add a mechanic to the ticket
@service_tickets_bp.route('/<int:ticket_id>/add-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("5/hour")
def add_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if ticket and mechanic:
        if mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)
            db.session.commit()
            return jsonify({
                "message": "mechanic added to ticket",
                "ticket": service_ticket_schema.dump(ticket),
                "mechanics": mechanics_schema.dump(ticket.mechanics)
            }), 200
        return jsonify({"message": "mechanic already assigned to ticket"}), 400
    return jsonify({"message": "ticket or mechanic not found"}), 404


# remove a mechanic from the ticket
@service_tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("5/hour")
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if ticket and mechanic:
        if mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)
            db.session.commit()
            return jsonify({
                "message": "mechanic removed from ticket",
                "ticket": service_ticket_schema.dump(ticket),
                "mechanics": mechanics_schema.dump(ticket.mechanics)
            }), 200
        return jsonify({"message": "invalid ID"}), 400
    return jsonify({"message": "ticket or mechanic not found"}), 400


@service_tickets_bp.route('/<int:ticket_id>/add-part/<int:part_id>', methods=['PUT'])
def add_part(ticket_id, part_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    part = db.session.get(SerializedPart, part_id)
    
    if ticket and part:
        if not part.ticket_id:
            ticket.serialized_parts.append(part)
            db.session.commit()
            return jsonify({
                "message": f"{part.description.part_name} added to ticket",
                "ticket": service_ticket_schema.dump(ticket),
                "parts": responses_schema.dump(ticket.serialized_parts)
            }), 200
        return jsonify({"message": "part already assigned to ticket"}), 400
    return jsonify({"message": "ticket or part not found"}), 404

# delete a ticket
@service_tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
@limiter.limit("5/hour")
def delete_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    
    if ticket:
        db.session.delete(ticket)
        db.session.commit()
        return jsonify({"message": "ticket deleted successfully"}), 200
    return jsonify({"message": "ticket not found"}), 404
