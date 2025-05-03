from app.extensions import ma
from app.models import Inventory




class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory

inventory_schema = InventorySchema()
inventorys_schema = InventorySchema(many=True)


