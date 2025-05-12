import unittest
from marshmallow import ValidationError
from app import create_app
from app.models import ServiceTicket, db, Mechanic
from app.utils.auth import encode_token
from werkzeug.security import generate_password_hash


class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanic(
            name="Test",
            email="test@email.com",
            address="123 Test St",
            salary=50000.0,
            password=generate_password_hash("password123")
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()

    def test_login(self):
        payload = {
            "email": "test@email.com",
            "password": "password123"
        }
        response = self.client.post('/mechanics/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)
        
    def test_create_mechanic(self):
        payload = {
            "name": "John Doe",
            "email": "john@email.com",
            "address": "456 Main St",
            "salary": 60000.0,
            "password": "password123"
        }
        response = self.client.post('/mechanics/', json=payload)
        self.assertRaises(ValidationError)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe")
            
    def test_create_invalid_mechanic(self):
        payload = {
            "name": "John Doe",
            "email": "john@email.com",
            "address": "456 Main St",
            "salary": 60000.0,
        }
        response = self.client.post('/mechanics/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.json)
            
    def test_get_mechanics(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], "Test")    
            
    def test_get_mechanic(self):
        response = self.client.get('/mechanics/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Test")
        
    def test_get_invalid_mechanic(self):
        response = self.client.get('/mechanics/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn("message", response.json)
        
    def test_update_mechanic(self):
        payload = {
            "name": "mary jane",
            "email": "mary@email.com",
            "address": "456 Main St",
            "salary": 60000.0,
            "password": "password123"
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.put('/mechanics/', json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "mary jane")
            
    def test_delete_mechanic(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.delete('/mechanics/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
    

def test_mechanic_activity(self):
    with self.app.app_context():
        ticket = ServiceTicket(
            service_desc="Brake repair",
            service_date="2025-05-09",
            vin="1HGCM82633A123456",
            mechanic_id=self.mechanic.id
        )
        db.session.add(ticket)
        db.session.commit()

    response = self.client.get('/mechanics/activity')

    self.assertEqual(response.status_code, 200)
    self.assertIn("mechanics", response.json)
    self.assertEqual(len(response.json["mechanics"]), 1)
 
def test_search_mechanic(self):
    payload = {
        "name": "Test"
    }
    response = self.client.post('/mechanics/search', json=payload)
    self.assertEqual(response.status_code, 200)
    self.assertIn("mechanics", response.json)
    self.assertEqual(len(response.json["mechanics"]), 1)
            
            
            
            
            
            
            
            
            
            
            
            
            