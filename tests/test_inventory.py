import unittest
from app import create_app
from app.models import db, Inventory

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.inventory = Inventory(
            part_name="Test",
            brand="TestBrand",
            price=100.0
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.inventory)
            db.session.commit()
            
        self.client = self.app.test_client()
    
    def test_get_paginated_inventory(self):
        response = self.client.get('/inventory/paginate?page=1&per_page=3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['items'][0]['part_name'], "Test")
        
    def test_create_inventory(self):
        payload = {
            "part_name": "New Part",
            "brand": "New Brand",
            "price": 150.0
        }
        
        response = self.client.post('/inventory/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part_name'], "New Part")
        
    def test_create_invalid_inventory(self):
        payload = {
            "part_name": "New Part",
            "brand": "New Brand"
        }
        
        response = self.client.post('/inventory/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("price", response.json)
        
        
    def test_get_inventory(self):
        response = self.client.get('/inventory/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], "Test")
        
        
    def test_get_invalid_inventory(self):
        response = self.client.get('/inventory/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn("message", response.json)
        
    def test_update_inventory(self):
        payload = {
            "part_name": "Updated Part",
            "brand": "Updated Brand",
            "price": 200.0
        }
        
        response = self.client.put('/inventory/1', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], "Updated Part")
        self.assertEqual(response.json['brand'], "Updated Brand")
        
        
    def test_delete_inventory(self):
        response = self.client.delete('/inventory/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
        
        
           