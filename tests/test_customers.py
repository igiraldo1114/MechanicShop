import unittest
from marshmallow import ValidationError
from app import create_app
from app.models import ServiceTicket, db, Customer
from app.utils.auth import encode_token
from werkzeug.security import generate_password_hash


class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.customer = Customer(
            name="Test",
            email="test@email.com",
            phone="1234567890",
            password=generate_password_hash("password123")
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()
        
    
    def test_login(self):
        payload = {
            "email": "test@email.com",
            "password": "password123"
        }
        response = self.client.post('/customers/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)
    
    
    def test_create_customer(self):
        payload = {
            "name": "John Doe",
            "email": "john@email.com",
            "phone": "0987654321",
            "password": "password123"
        }
        
        response = self.client.post('/customers/', json=payload)
        self.assertRaises(ValidationError)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe")


    def test_create_invalid_customer(self):
        payload = {
            "name": "John Doe",
            "email": "john@email.com",
            "password": "0987654321",
        }
        response = self.client.post('/customers/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone", response.json)

            
    def test_get_customers(self):
        response = self.client.get('/customers/paginate?page=1&per_page=3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['customers'][0]['name'], "Test")  
        
        
    def test_get_customer(self):
        response = self.client.get('/customers/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Test")
        
    
    def test_get_invalid_customer(self):
        response = self.client.get('/customers/999')
        self.assertEqual(response.status_code, 404)        
        
    def test_customer_update(self):
        update_payload = {
            "name": "mary jane",
            "email": "mary@email.com",
            "phone": "0987654321",
            "password": "password123"
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        
    def test_delete_customer(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.delete('/customers/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Customer deleted successfully")
        
def test_my_tickets_with_tickets(self):
    with self.app.app_context():
        customer = db.session.get(Customer, self.customer.id)

        ticket = ServiceTicket(
            service_desc="Oil change",
            service_date="2025-05-09",
            vin="BDHJWBDJ4BE0EBDUIBFE78",
            customer_id=customer.id
        )
        db.session.add(ticket)
        db.session.commit()

    headers = {"Authorization": f"Bearer {self.token}"}
    response = self.client.get('/customers/my-tickets', headers=headers)

    self.assertEqual(response.status_code, 200)
    self.assertIn("tickets", response.json)
    self.assertEqual(len(response.json["tickets"]), 1)
    self.assertEqual(response.json["tickets"][0], "Oil change")
            
def test_search_customers(self):
    with self.app.app_context():
        customer = Customer(
            name="John wick",
            email="john.wick@email.com",
            phone="1234567890",
            password=generate_password_hash("password123")
        )
        db.session.add(customer)
        db.session.commit()

    response = self.client.get('/customers/search?search=john.wick@email.com')

    self.assertEqual(response.status_code, 200)
    self.assertIn("customers", response.json)
    self.assertEqual(len(response.json["customers"]), 1)
    self.assertEqual(response.json["customers"][0]["email"], "john.doe@email.com")     
        
        