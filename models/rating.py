from sqlalchemy import Column, Integer, String
from database.connection import Base


class Rating(Base):
    __tablename__ = "rating"

    id = Column(Integer, primary_key=True)
    rating = Column(Integer, default=None)
    description = Column(String(500), default=None)
