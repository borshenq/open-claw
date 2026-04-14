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

    # Relationships
    reports = relationship("RepairRequest", back_populates="reporter", foreign_keys="RepairRequest.reporter_id")
    assignments = relationship("RepairRequest", back_populates="assigned_to", foreign_keys="RepairRequest.assigned_to_id")

class RepairRequest(Base):
    __tablename__ = "repair_requests"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=True)
    status = Column(String(20), default="Pending") # Pending, In Progress, Completed
    
    # New fields
    priority = Column(String(20), default="Normal") # Low, Normal, High, Urgent
    category = Column(String(50), default="General") # Electrical, Plumbing, Furniture, IT, General
    rating = Column(Integer, nullable=True) # 1-5
    feedback = Column(Text, nullable=True)
    estimated_completion_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # New: Link to user who reported it
    reporter_id = Column(Integer, ForeignKey("users.id"))
    reporter = relationship("User", back_populates="reports", foreign_keys=[reporter_id])

    # New: Assigned technician
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to = relationship("User", back_populates="assignments", foreign_keys=[assigned_to_id])

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
