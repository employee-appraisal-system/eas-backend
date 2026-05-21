from sqlalchemy import Column, Integer, String, ForeignKey
from database.connection import Base
from sqlalchemy.orm import column_property


class Employee(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True)

    first_name = Column(String(45))
    last_name = Column(String(45))
    full_name = column_property(first_name + " " + last_name)

    email = Column(String(55), nullable=False)
    password = Column(String(256))

    role = Column(String(50), nullable=False)

    manager_id = Column(Integer, ForeignKey("employee.id"))
    previous_manager_id = Column(Integer, ForeignKey("employee.id"))
