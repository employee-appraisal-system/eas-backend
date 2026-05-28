from database.connection import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship


class EmployeeAllocation(Base):
    __tablename__ = "appraisal_cycle_allocation"

    allocation_id = Column(Integer, primary_key=True, autoincrement=True)
    cycle_id = Column(
        Integer,
        ForeignKey("appraisal_cycle.cycle_id", ondelete="CASCADE"),
        nullable=False,
    )
    employee_id = Column(
        Integer, ForeignKey("employee.id", ondelete="CASCADE"), nullable=False
    )

    employee = relationship("Employee")
    cycle = relationship("AppraisalCycle")
