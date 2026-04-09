#!/usr/bin/env python3
"""
📅 Scheduler AI Agent - Generic Version
Verwaltet Termine, Buchungen und Erinnerungen
"""
import json
import os
from datetime import datetime, timedelta

CONFIG_FILE = "config/scheduler_config.json"
APPOINTMENTS_FILE = "data/appointments.json"
REMINDERS_FILE = "data/reminders.json"

DEFAULT_CONFIG = {
    "business_name": "Unser Unternehmen",
    "timezone": "Europe/Berlin",
    "working_hours": {
        "monday": {"start": "09:00", "end": "18:00"},
        "tuesday": {"start": "09:00", "end": "18:00"},
        "wednesday": {"start": "09:00", "end": "18:00"},
        "thursday": {"start": "09:00", "end": "18:00"},
        "friday": {"start": "09:00", "end": "18:00"},
        "saturday": {"start": "10:00", "end": "14:00"},
        "sunday": None  # Closed
    },
    "slot_duration_minutes": 30,
    "buffer_between_slots": 10,
    "max_days_advance": 30
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return DEFAULT_CONFIG

def load_appointments():
    if os.path.exists(APPOINTMENTS_FILE):
        with open(APPOINTMENTS_FILE) as f:
            return json.load(f)
    return []

def save_appointments(appointments):
    os.makedirs(os.path.dirname(APPOINTMENTS_FILE), exist_ok=True)
    with open(APPOINTMENTS_FILE, 'w') as f:
        json.dump(appointments, f, indent=2)

def get_available_slots(date_str, duration_minutes=30):
    """Liefere verfügbare Zeitfenster für einen Tag"""
    config = load_config()
    appointments = load_appointments()
    
    day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A").lower()
    hours = config["working_hours"].get(day_name)
    
    if not hours:
        return []  # Geschlossen
    
    start_time = datetime.strptime(hours["start"], "%H:%M")
    end_time = datetime.strptime(hours["end"], "%H:%M")
    
    # Generate all possible slots
    slots = []
    current = start_time
    while current + timedelta(minutes=duration_minutes) <= end_time:
        slot_start = current.strftime("%H:%M")
        slot_end = (current + timedelta(minutes=duration_minutes)).strftime("%H:%M")
        
        # Check if slot is already booked
        is_booked = any(
            a.get("date") == date_str and a.get("time") == slot_start and a.get("status") == "confirmed"
            for a in appointments
        )
        
        if not is_booked:
            slots.append({"date": date_str, "time": slot_start, "end": slot_end})
        
        current += timedelta(minutes=duration_minutes + config["buffer_between_slots"])
    
    return slots

def book_appointment(customer_name, customer_email, date_str, time_str, service="Standard"):
    """Termin buchen"""
    appointments = load_appointments()
    
    # Check if slot is available
    is_available = not any(
        a.get("date") == date_str and a.get("time") == time_str and a.get("status") == "confirmed"
        for a in appointments
    )
    
    if not is_available:
        return {"success": False, "error": "Slot bereits gebucht"}
    
    appointment = {
        "id": len(appointments) + 1,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "date": date_str,
        "time": time_str,
        "service": service,
        "status": "confirmed",
        "created_at": datetime.now().isoformat(),
        "reminder_sent": False
    }
    
    appointments.append(appointment)
    save_appointments(appointments)
    
    return {
        "success": True,
        "appointment": appointment,
        "message": f"✅ Termin gebucht für {date_str} um {time_str}"
    }

def cancel_appointment(appointment_id):
    """Termin stornieren"""
    appointments = load_appointments()
    
    for appt in appointments:
        if appt["id"] == appointment_id:
            appt["status"] = "cancelled"
            save_appointments(appointments)
            return {"success": True, "message": "Termin storniert"}
    
    return {"success": False, "error": "Termin nicht gefunden"}

def get_upcoming_appointments(days=7):
    """Alle anstehenden Termine"""
    appointments = load_appointments()
    today = datetime.now().date()
    end_date = today + timedelta(days=days)
    
    upcoming = []
    for appt in appointments:
        if appt["status"] == "confirmed":
            appt_date = datetime.strptime(appt["date"], "%Y-%m-%d").date()
            if today <= appt_date <= end_date:
                upcoming.append(appt)
    
    return sorted(upcoming, key=lambda x: (x["date"], x["time"]))

def send_reminders():
    """Sende Erinnerungen für morgige Termine"""
    appointments = load_appointments()
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    reminders_sent = 0
    for appt in appointments:
        if appt["date"] == tomorrow and not appt.get("reminder_sent"):
            # In production: send actual email/SMS
            print(f"📧 Erinnerung an {appt['customer_name']} für {appt['date']} um {appt['time']}")
            appt["reminder_sent"] = True
            reminders_sent += 1
    
    if reminders_sent > 0:
        save_appointments(appointments)
    
    return reminders_sent

if __name__ == "__main__":
    print("📅 Scheduler Agent gestartet...")
    
    # Test: Show available slots for today
    today = datetime.now().strftime("%Y-%m-%d")
    slots = get_available_slots(today)
    print(f"📅 Heute verfügbare Slots: {len(slots)}")
    
    # Show upcoming appointments
    upcoming = get_upcoming_appointments()
    print(f"📋 Anstehende Termine: {len(upcoming)}")
    
    # Send reminders
    sent = send_reminders()
    print(f"📧 Erinnerungen gesendet: {sent}")
    
    print("✅ Scheduler Agent fertig")
