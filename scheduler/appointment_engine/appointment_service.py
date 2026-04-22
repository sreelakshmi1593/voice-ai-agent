from sqlalchemy.orm import Session
from database import Appointment, DoctorSchedule, SessionLocal
import datetime

# Sample doctors data
DOCTORS = {
    "cardiologist": ["Dr. Sharma", "Dr. Reddy"],
    "dermatologist": ["Dr. Priya", "Dr. Mehta"],
    "general": ["Dr. Kumar", "Dr. Singh"],
    "orthopedic": ["Dr. Rao", "Dr. Gupta"],
    "pediatrician": ["Dr. Nair", "Dr. Iyer"]
}

AVAILABLE_SLOTS = ["09:00 AM", "10:00 AM", "11:00 AM", 
                   "02:00 PM", "03:00 PM", "04:00 PM"]

def get_available_slots(specialization: str, date: str):
    db = SessionLocal()
    booked = db.query(Appointment).filter(
        Appointment.specialization == specialization,
        Appointment.date == date,
        Appointment.status == "confirmed"
    ).all()
    booked_times = [a.time for a in booked]
    available = [s for s in AVAILABLE_SLOTS if s not in booked_times]
    db.close()
    return available

def book_appointment(patient_name: str, patient_id: str, 
                     specialization: str, date: str, 
                     time: str, language: str):
    db = SessionLocal()
    
    # Check if slot already booked
    existing = db.query(Appointment).filter(
        Appointment.specialization == specialization,
        Appointment.date == date,
        Appointment.time == time,
        Appointment.status == "confirmed"
    ).first()
    
    if existing:
        db.close()
        return {"success": False, "message": "Slot already booked"}
    
    # Check past time
    try:
        appointment_datetime = datetime.datetime.strptime(
            f"{date} {time}", "%Y-%m-%d %I:%M %p"
        )
        if appointment_datetime < datetime.datetime.now():
            db.close()
            return {"success": False, "message": "Cannot book past time"}
    except:
        pass
    
    # Get doctor name
    doctors = DOCTORS.get(specialization.lower(), ["Dr. Kumar"])
    doctor_name = doctors[0]
    
    # Create appointment
    appointment = Appointment(
        patient_name=patient_name,
        patient_id=patient_id,
        doctor_name=doctor_name,
        specialization=specialization,
        date=date,
        time=time,
        language=language,
        status="confirmed"
    )
    db.add(appointment)
    db.commit()
    db.close()
    
    return {
        "success": True,
        "message": f"Appointment booked with {doctor_name}",
        "doctor": doctor_name,
        "date": date,
        "time": time
    }

def cancel_appointment(patient_id: str, date: str, time: str):
    db = SessionLocal()
    appointment = db.query(Appointment).filter(
        Appointment.patient_id == patient_id,
        Appointment.date == date,
        Appointment.time == time,
        Appointment.status == "confirmed"
    ).first()
    
    if not appointment:
        db.close()
        return {"success": False, "message": "Appointment not found"}
    
    appointment.status = "cancelled"
    db.commit()
    db.close()
    return {"success": True, "message": "Appointment cancelled successfully"}

def reschedule_appointment(patient_id: str, old_date: str, 
                           old_time: str, new_date: str, new_time: str):
    db = SessionLocal()
    appointment = db.query(Appointment).filter(
        Appointment.patient_id == patient_id,
        Appointment.date == old_date,
        Appointment.time == old_time,
        Appointment.status == "confirmed"
    ).first()
    
    if not appointment:
        db.close()
        return {"success": False, "message": "Appointment not found"}
    
    appointment.date = new_date
    appointment.time = new_time
    db.commit()
    db.close()
    return {"success": True, "message": f"Rescheduled to {new_date} at {new_time}"}

def get_patient_appointments(patient_id: str):
    db = SessionLocal()
    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient_id,
        Appointment.status == "confirmed"
    ).all()
    db.close()
    return appointments