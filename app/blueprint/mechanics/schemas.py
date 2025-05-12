from app.extensions import ma
from app.models import Mechanic
from marshmallow import fields




class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        include_relationships = True
    
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)

mechanic_login_schema = MechanicSchema(exclude=['name', 'address', 'salary'])



class MechanicActivitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        include_relationships = True
        
mechanic_activity_schema = MechanicActivitySchema(many =True)