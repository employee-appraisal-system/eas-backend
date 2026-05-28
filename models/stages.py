from database.connection import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, text
from sqlalchemy.orm import relationship


class Stage(Base):
    __tablename__ = "appraisal_stage"

    stage_id = Column(Integer, primary_key=True, autoincrement=True)
    stage_name = Column(String(50), nullable=False)
    cycle_id = Column(
        Integer,
        ForeignKey("appraisal_cycle.cycle_id", ondelete="CASCADE"),
        nullable=True,
    )
    start_date_of_stage = Column(Date, nullable=True)
    end_date_of_stage = Column(Date, nullable=True)
    is_active = Column(Boolean, default=False)
    is_completed = Column(Boolean, server_default=text("false"))
    cycle = relationship("AppraisalCycle", back_populates="stages")
