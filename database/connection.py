from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Create database engine
engine = create_engine(DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model class
Base = declarative_base()


def get_db():
    db = (
        SessionLocal()
    )  # FastAPI calls the function and gets the session from sessionLocal
    try:
        yield db  # Then it temporarily pause and use this session (inject it into route)
    finally:
        db.close()  # After the use is done, it comes back and close the session
