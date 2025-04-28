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
    
    

class Mechanic(Base):
    __tablename__ = "mechanics"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(150), nullable=False)
    address: Mapped[str] = mapped_column(db.String(100), nullable=False)
    salary: Mapped[float] = mapped_column(db.Float)
    
    tickets: Mapped[list["ServiceTicket"]] = db.relationship(secondary=service_mechanic, back_populates="mechanics")
    