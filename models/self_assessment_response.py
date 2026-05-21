from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base


class SelfAssessmentResponse(Base):
    __tablename__ = "self_assessment_response"

    response_id = Column(Integer, primary_key=True, autoincrement=True)
    allocation_id = Column(
        Integer, ForeignKey("employee_allocation.allocation_id", ondelete="CASCADE")
    )
    cycle_id = Column(
        Integer, ForeignKey("appraisal_cycle.cycle_id", ondelete="CASCADE")
    )
    employee_id = Column(Integer, ForeignKey("employee.id", ondelete="CASCADE"))
    question_id = Column(
        Integer, ForeignKey("question.question_id", ondelete="CASCADE")
    )
    option_id = Column(Integer, ForeignKey("option.option_id", ondelete="CASCADE"))
    response_text = Column(Text)

    question = relationship("Question", backref="responses")
    option = relationship("Option", backref="responses", lazy="joined")
