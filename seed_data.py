import sys
import os
from datetime import datetime, timedelta

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import models, database, auth
from sqlalchemy.orm import Session

def seed():
    # Ensure tables are created
    print("Initializing database tables...")
    models.Base.metadata.create_all(bind=database.engine)
    
    db = next(database.get_db())
    
    # 1. Create Users
    print("Creating users...")
    # Check if users exist
    reporter_user = db.query(models.User).filter(models.User.username == "student1").first()
    if not reporter_user:
        reporter_user = models.User(
            username="student1",
            email="student1@example.edu",
            hashed_password=auth.get_password_hash("password123"),
            role="Reporter"
        )
        db.add(reporter_user)
    
    tech_user = db.query(models.User).filter(models.User.username == "admin").first()
    if not tech_user:
        tech_user = models.User(
            username="admin",
            email="admin@example.edu",
            hashed_password=auth.get_password_hash("admin123"),
            role="Technician"
        )
        db.add(tech_user)
    
    db.commit()
    db.refresh(reporter_user)
    
    # 2. Create 10 Repair Requests
    print("Creating 10 repair requests...")
    test_data = [
        ("Air Conditioner", "Room 302", "Making loud noise and not cooling.", "Completed"),
        ("Projector", "Classroom 1A", "Lamp is broken, won't turn on.", "In Progress"),
        ("Ceiling Light", "Library 2F", "Flickering constantly.", "Pending"),
        ("Water Fountain", "Gym Entrance", "Leaking water on the floor.", "In Progress"),
        ("Desktop PC", "Computer Lab B", "Blue screen of death on startup.", "Pending"),
        ("Window Handle", "Room 205", "Stuck and cannot be closed.", "Completed"),
        ("Door Lock", "Music Room", "Key gets stuck in the cylinder.", "Pending"),
        ("Whiteboard", "Room 401", "Surface is peeling off.", "Pending"),
        ("Toilet Flush", "Men's Restroom 1F", "Continuous running water.", "In Progress"),
        ("Wi-Fi Router", "Student Lounge", "Connection keeps dropping every 5 mins.", "Pending"),
    ]
    
    for i, (item, loc, desc, status) in enumerate(test_data):
        # Create request
        req = models.RepairRequest(
            item_name=item,
            location=loc,
            description=desc,
            status=status,
            reporter_id=reporter_user.id,
            created_at=datetime.utcnow() - timedelta(days=i)
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        
        # Add some logs for non-pending items
        if status == "In Progress":
            log = models.RepairLog(
                request_id=req.id,
                note="Technician inspected. Parts ordered.",
                updated_at=datetime.utcnow() - timedelta(hours=5)
            )
            db.add(log)
        elif status == "Completed":
            log1 = models.RepairLog(
                request_id=req.id,
                note="Technician identified the issue.",
                updated_at=datetime.utcnow() - timedelta(days=1)
            )
            log2 = models.RepairLog(
                request_id=req.id,
                note="Repair finished. Tested and working fine.",
                updated_at=datetime.utcnow() - timedelta(hours=2)
            )
            db.add(log1)
            db.add(log2)
    
    db.commit()
    print("Successfully seeded 10 test records!")

if __name__ == "__main__":
    seed()
