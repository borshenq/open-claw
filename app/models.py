from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="Reporter") # Reporter, Technician

    # Relationship to reports
    reports = relationship("RepairRequest", back_populates="reporter")

class RepairRequest(Base):
    __tablename__ = "repair_requests"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=True)
    status = Column(String(20), default="Pending") # Pending, In Progress, Completed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # New: Link to user who reported it
    reporter_id = Column(Integer, ForeignKey("users.id"))
    reporter = relationship("User", back_populates="reports")

    # Relationship to progress logs
    logs = relationship("RepairLog", back_populates="request", cascade="all, delete-orphan")

class RepairLog(Base):
    __tablename__ = "repair_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("repair_requests.id"))
    note = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to the request
    request = relationship("RepairRequest", back_populates="logs")
