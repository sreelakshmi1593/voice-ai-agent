from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    patient_name = Column(String)
    patient_id = Column(String)
    doctor_name = Column(String)
    specialization = Column(String)
    date = Column(String)
    time = Column(String)
    language = Column(String)
    status = Column(String, default="confirmed")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DoctorSchedule(Base):
    __tablename__ = "doctor_schedule"
    id = Column(Integer, primary_key=True)
    doctor_name = Column(String)
    specialization = Column(String)
    date = Column(String)
    available_slots = Column(String)

# Create database
engine = create_engine("sqlite:///appointments.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()