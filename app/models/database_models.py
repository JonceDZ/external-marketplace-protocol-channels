from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.db.database import Base

class LogEntry(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    Operation = Column(String, nullable=False)
    Direction = Column(String, nullable=False)
    ContentSource = Column(Text, nullable=True)
    ContentTranslated = Column(Text, nullable=True)
    ContentDestination = Column(Text, nullable=True)
    BusinessMessage = Column(Text, nullable=True)
    Status = Column(String, nullable=False)
    Timestamp = Column(DateTime, default=datetime.utcnow)
