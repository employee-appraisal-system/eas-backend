from sqlalchemy import Column, Integer, String, ForeignKey
from database.connection import Base


class Employee(Base):
    __tablename__ = "employee"

    employee_id = Column(Integer, primary_key=True, index=True)
    role_id = Column(String(30), nullable=True, unique=True)
    employee_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    reporting_manager = Column(
        Integer, ForeignKey("employee.employee_id", ondelete="SET NULL"), nullable=True
    )
    previous_reporting_manager = Column(
        Integer, ForeignKey("employee.employee_id", ondelete="SET NULL"), nullable=True
    )
    password = Column(String(10), nullable=False)
