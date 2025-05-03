from app.extensions import ma
from app.models import SerializedPart




class SerializedPartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SerializedPart
        include_fk = True
        # include_relationships = True

serialized_part_schema = SerializedPartSchema()
serialized_parts_schema = SerializedPartSchema(many=True)

