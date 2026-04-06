from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./meetmind.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    transcript = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)   # JSON string
    key_points = Column(Text, nullable=True)     # JSON string
    participants = Column(Text, nullable=True)   # JSON string
    sentiment = Column(Text, nullable=True)      # JSON string
    meeting_type = Column(String(100), nullable=True)
    duration_estimate = Column(String(50), nullable=True)
    topic = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
