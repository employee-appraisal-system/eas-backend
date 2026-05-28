from database.connection import Base
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


class QuestionAssignment(Base):
    __tablename__ = "appraisal_question_assignment"

    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        Integer, ForeignKey("employee.id", ondelete="CASCADE"), nullable=False
    )
    question_id = Column(
        Integer,
        ForeignKey("appraisal_question.question_id", ondelete="CASCADE"),
        nullable=False,
    )
    cycle_id = Column(
        Integer,
        ForeignKey("appraisal_cycle.cycle_id", ondelete="CASCADE"),
        nullable=False,
    )

    employee = relationship("Employee")
    question = relationship("Question")
    cycle = relationship("AppraisalCycle")

    __table_args__ = (
        UniqueConstraint(
            "employee_id", "question_id", "cycle_id", name="uq_employee_question_cycle"
        ),
    )
