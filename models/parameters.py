from database.connection import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship


class Parameter(Base):
    __tablename__ = "appraisal_parameter"

    parameter_id = Column(Integer, primary_key=True, autoincrement=True)
    parameter_title = Column(String(255), nullable=False)
    helptext = Column(Text)
    cycle_id = Column(
        Integer,
        ForeignKey("appraisal_cycle.cycle_id", ondelete="CASCADE"),
        nullable=True,
    )
    applicable_to_employee = Column(Boolean)
    applicable_to_lead = Column(Boolean)
    is_fixed_parameter = Column(Boolean)
    cycle = relationship("AppraisalCycle", back_populates="parameters")
