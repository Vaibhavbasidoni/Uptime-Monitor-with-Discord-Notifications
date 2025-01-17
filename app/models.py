from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Website(Base):
    __tablename__ = "websites"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    check_interval_seconds = Column(Integer, default=300)
    expected_status_code = Column(Integer, default=200)
    created_at = Column(DateTime, default=datetime.utcnow)

class StatusCheck(Base):
    __tablename__ = "status_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"))
    status = Column(String)  # "up" or "down"
    response_time_ms = Column(Float, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow)
    error_message = Column(String, nullable=True)
    last_status_change = Column(DateTime, nullable=True)

class DiscordWebhook(Base):
    __tablename__ = "discord_webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True)
    name = Column(String, nullable=True) 