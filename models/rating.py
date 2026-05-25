from sqlalchemy import Column, Integer, String, ForeignKey
from database.connection import Base
from sqlalchemy.orm import column_property

class Rating(Base):
    __tablename__ = "rating"

    id = Column(Integer, primary_key=True)
    rating = Column(Integer, default=None)
    description = Column(String(500), default=None)