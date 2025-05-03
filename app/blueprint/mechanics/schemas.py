from app.extensions import ma
from app.models import Mechanic




class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)

login_schema = MechanicSchema(exclude=['name', 'address', 'salary'])



class MechanicActivitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        include_relationships = True
        
mechanic_activity_schema = MechanicActivitySchema(many =True)