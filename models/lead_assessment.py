from sqlalchemy import Column, Integer, ForeignKey, Text, Date
from database.connection import Base


class LeadAssessmentRating(Base):
    __tablename__ = "lead_assessment_rating"

    lead_rating_id = Column(Integer, primary_key=True, index=True)
    allocation_id = Column(
        Integer, ForeignKey("employee_allocation.allocation_id", ondelete="CASCADE")
    )
    cycle_id = Column(
        Integer, ForeignKey("appraisal_cycle.cycle_id", ondelete="CASCADE")
    )
    employee_id = Column(
        Integer, ForeignKey("employee.employee_id", ondelete="CASCADE")
    )
    parameter_id = Column(
        Integer, ForeignKey("parameters.parameter_id", ondelete="CASCADE")
    )
    parameter_rating = Column(Integer, nullable=False)
    specific_input = Column(Text, nullable=True)
    discussion_date = Column(Date, nullable=False)
