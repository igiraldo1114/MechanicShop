import unittest
from app import create_app
from app.models import Customer, Mechanic, db, ServiceTicket, Inventory, SerializedPart
from werkzeug.security import generate_password_hash
from datetime import date


class TestServiceTicket(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.app_context = self.app.app_context()  
        self.app_context.push() 

        db.drop_all()
        db.create_all()

        self.customer = Customer(
            name="John Doe",
            email="johndoe@example.com",
            phone="123-456-7890",
            password=generate_password_hash("password123")
        )
        db.session.add(self.customer)
        db.session.commit()

        self.mechanic = Mechanic(
            name="Jane Smith",
            email="janesmith@example.com",
            address="123 Mechanic St",
            salary=50000.0,
            password=generate_password_hash("password123")
        )
        db.session.add(self.mechanic)
        db.session.commit()

        self.inventory_part = Inventory(
            part_name="Brake Pad",
            brand="AutoBrand",
            price=50.0
        )
        db.session.add(self.inventory_part)
        db.session.commit()

        self.serialized_part = SerializedPart(
            desc_id=self.inventory_part.id
        )
        db.session.add(self.serialized_part)

        self.service_ticket = ServiceTicket(
            service_desc="Test service",
            service_date=date(2025, 10, 1),
            vin="1HGCM82633A123456",
            customer_id=self.customer.id
        )
        db.session.add(self.service_ticket)
        db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()  
    
    
    def test_create_service_ticket(self):
        payload = {
            "service_desc": "Oil Change",
            "service_date": "2023-10-01",
            "vin": "1HGCM82633A123456",
            "customer_id": 1
        }

        response = self.client.post('/service-ticket/', json=payload)
        self.assertEqual(response.status_code, 201)

    def test_create_invalid_service_ticket(self):
        payload = {
            "service_desc": "Oil Change",
            "service_date": "2023-10-01",
            "vin": "1HGCM82633A123456",
        }
        response = self.client.post('/service-ticket/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("customer_id", response.json)

    
    def test_get_service_tickets(self):
        response = self.client.get('/service-ticket/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['service_desc'], "Test service")

    def test_get_service_ticket(self):
        response = self.client.get(f'/service-ticket/{self.service_ticket.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['service_desc'], "Test service")

    def test_add_mechanic_to_ticket(self):
        response = self.client.put(f'/service-ticket/{self.service_ticket.id}/add-mechanic/{self.mechanic.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)

    def test_remove_mechanic_from_ticket(self):
        self.service_ticket.mechanics.append(self.mechanic)
        db.session.commit()

        response = self.client.put(f'/service-ticket/{self.service_ticket.id}/remove-mechanic/{self.mechanic.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
        
    
    def test_add_part_to_ticket(self):
        response = self.client.put(f'/service-ticket/{self.service_ticket.id}/add-part/{self.serialized_part.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
        
    def test_delete_service_ticket(self):
        response = self.client.delete(f'/service-ticket/{self.service_ticket.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
        
 