from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    filing_number = Column(String(100), unique=True)
    status = Column(String(50))
    filing_date = Column(DateTime)
    state_of_formation = Column(String(100))
    principal_address = Column(Text)
    mailing_address = Column(Text)
    registered_agent_name = Column(String(255))
    registered_agent_address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    filing_history = relationship("FilingHistory", back_populates="business")


class FilingHistory(Base):
    __tablename__ = "filing_histories"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    filing_type = Column(String)
    filing_date = Column(Date)
    document_url = Column(String)

    business = relationship("Business", back_populates="filing_history") 