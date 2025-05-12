import unittest
from app import create_app
from app.models import db, SerializedPart, Inventory


class TestSerializedPart(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.app_context = self.app.app_context()  
        self.app_context.push()  

        db.drop_all()
        db.create_all()

        self.inventory_part = Inventory(
            part_name="Test Part",
            brand="Test Brand",
            price=100.0
        )
        db.session.add(self.inventory_part)
        db.session.commit()

        self.serialized_part = SerializedPart(
            desc_id=self.inventory_part.id
        )
        db.session.add(self.serialized_part)
        db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()  

    def test_get_paginated_serialized_parts(self):
        response = self.client.get('/serialized-part/paginate?page=1&per_page=3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['parts'][0]['desc_id'], self.serialized_part.desc_id)

    def test_create_serialized_part(self):
        payload = {
            "desc_id": 1
        }

        response = self.client.post('/serialized-part/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part']['desc_id'], self.inventory_part.id)

    def test_get_stock_serialized_part(self):
        response = self.client.get(f'/serialized-part/stock/{self.serialized_part.desc_id}')
        self.assertEqual(response.status_code, 200)

    def test_delete_serialized_part(self):
        response = self.client.delete(f'/serialized-part/{self.serialized_part.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
            