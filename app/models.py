from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date



class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


service_mechanic = db.Table(
    'service_mechanic', 
    Base.metadata,
    db.Column('ticket_id', db.ForeignKey('service_tickets.id')),
    db.Column('mechanic_id', db.ForeignKey('mechanics.id'))
)

class Customer(Base):
    __tablename__ = "customers"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(150), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)
    
    tickets: Mapped[list["ServiceTicket"]] = db.relationship(back_populates="customer")
    

class ServiceTicket(Base):
    __tablename__ = "service_tickets"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    service_desc: Mapped[str] = mapped_column(db.String(200))
    service_date: Mapped[date]
    vin: Mapped[str] = mapped_column(db.String(100))
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id"), nullable=False)  
    
    customer: Mapped["Customer"] = db.relationship(back_populates="tickets")
    mechanics: Mapped[list["Mechanic"]] = db.relationship(secondary=service_mechanic, back_populates="tickets")
    serialized_parts: Mapped[list["SerializedPart"]] = db.relationship(back_populates="ticket")
    
    

class Mechanic(Base):
    __tablename__ = "mechanics"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(150), nullable=False)
    address: Mapped[str] = mapped_column(db.String(100), nullable=False)
    salary: Mapped[float] = mapped_column(db.Float)
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)
    
    tickets: Mapped[list["ServiceTicket"]] = db.relationship(secondary=service_mechanic, back_populates="mechanics")
    
    
class Inventory(Base):
    __tablename__ = "inventory"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    part_name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    brand: Mapped[str] = mapped_column(db.String(100), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)
    
    serialized_parts: Mapped[list["SerializedPart"]] = db.relationship(back_populates="description")
    

class SerializedPart(Base):
    __tablename__ = "serialized_parts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    desc_id: Mapped[int] = mapped_column(db.ForeignKey("inventory.id"), nullable=False)
    ticket_id: Mapped[int] = mapped_column(db.ForeignKey("service_tickets.id"), nullable=True)
    
    description: Mapped["Inventory"] = db.relationship(back_populates="serialized_parts")
    ticket: Mapped["ServiceTicket"] = db.relationship(back_populates="serialized_parts")
    
