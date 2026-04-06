#!/usr/bin/env python3
"""
PetCare Agent
Handles pet sitting, grooming appointments, feeding schedules, vet visits.
"""
import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("openclaw.petcare")

DATA_DIR = Path.home() / ".openclaw" / "workspace" / "data" / "petcare"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SCHEDULE_FILE = DATA_DIR / "schedule.json"
PETS_FILE = DATA_DIR / "pets.json"
APPOINTMENTS_FILE = DATA_DIR / "appointments.json"


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception as e:
            log.warning("Failed to load %s: %s", path, e)
    return default


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, default=str))


@dataclass
class Pet:
    name: str
    species: str  # dog, cat, bird, fish, reptile, other
    breed: str = ""
    birth_date: str = ""
    weight_kg: float = 0.0
    food: str = ""
    food_amount: str = ""
    feeding_times: list = field(default_factory=list)
    medications: list = field(default_factory=list)
    vet_name: str = ""
    vet_phone: str = ""
    notes: str = ""


@dataclass
class Appointment:
    pet_name: str
    type: str  # grooming, vet, boarding, walking, sitting, other
    date: str
    time: str = ""
    location: str = ""
    contact: str = ""
    cost: float = 0.0
    notes: str = ""
    status: str = "scheduled"  # scheduled, completed, cancelled


class PetCareAgent:
    def __init__(self):
        self.pets = load_json(PETS_FILE, {})
        self.schedule = load_json(SCHEDULE_FILE, {})
        self.appointments = load_json(APPOINTMENTS_FILE, [])

    # ── Pet Management ──────────────────────────────────────────

    def add_pet(self, name: str, species: str, **kwargs):
        pet = Pet(name=name, species=species.lower(), **kwargs)
        self.pets[name] = vars(pet)
        save_json(PETS_FILE, self.pets)
        log.info("Added pet: %s (%s)", name, species)
        return f"✅ Pet '{name}' added."

    def list_pets(self):
        if not self.pets:
            return "No pets registered. Add one with: petcare add-pet --name Max --species dog"
        lines = ["🐾 Registered Pets:", ""]
        for name, data in self.pets.items():
            lines.append(f"  • {name} ({data['species']}) — {data.get('breed', 'unknown breed')}")
            if data.get('feeding_times'):
                lines.append(f"    Feed at: {', '.join(data['feeding_times'])}")
            if data.get('medications'):
                lines.append(f"    Meds: {', '.join(data['medications'])}")
        return "\n".join(lines)

    def remove_pet(self, name: str):
        if name in self.pets:
            del self.pets[name]
            save_json(PETS_FILE, self.pets)
            log.info("Removed pet: %s", name)
            return f"✅ Pet '{name}' removed."
        return f"❌ Pet '{name}' not found."

    # ── Appointments ────────────────────────────────────────────

    def add_appointment(self, pet_name: str, appt_type: str, date: str, time: str = "",
                        location: str = "", contact: str = "", cost: float = 0.0, notes: str = ""):
        appt = Appointment(pet_name=pet_name, type=appt_type.lower(), date=date,
                           time=time, location=location, contact=contact, cost=cost, notes=notes)
        self.appointments.append(vars(appt))
        save_json(APPOINTMENTS_FILE, self.appointments)
        log.info("Added appointment for %s: %s on %s", pet_name, appt_type, date)
        return f"📅 Appointment for '{pet_name}' ({appt_type}) on {date} added."

    def list_appointments(self, pet_name: str = ""):
        filtered = self.appointments
        if pet_name:
            filtered = [a for a in self.appointments if a['pet_name'].lower() == pet_name.lower()]
        if not filtered:
            return "No appointments found."
        lines = ["📅 Appointments:", ""]
        for a in filtered:
            status_icon = {"scheduled": "📆", "completed": "✅", "cancelled": "❌"}.get(a['status'], "📆")
            lines.append(f"  {status_icon} {a['pet_name']} — {a['type']} | {a['date']} {a['time']} | {a['location']}")
        return "\n".join(lines)

    # ── Feeding Reminders ────────────────────────────────────────

    def feeding_schedule(self, pet_name: str = ""):
        pets = {pet_name: self.pets[pet_name]} if pet_name and pet_name in self.pets else self.pets
        if not pets:
            return "No pets found."
        lines = ["🍖 Feeding Schedule:", ""]
        for name, data in pets.items():
            times = data.get('feeding_times', [])
            food = data.get('food', '')
            amount = data.get('food_amount', '')
            if times:
                lines.append(f"  {name}: {', '.join(times)} → {food} ({amount})")
            else:
                lines.append(f"  {name}: No schedule set")
        return "\n".join(lines)

    # ── Care Report ────────────────────────────────────────────

    def care_report(self) -> str:
        lines = ["🐾 PetCare Report — " + datetime.now().strftime("%Y-%m-%d %H:%M"), ""]
        lines.append(self.list_pets() + "\n")
        lines.append(self.feeding_schedule() + "\n")
        upcoming = [a for a in self.appointments if a['status'] == 'scheduled']
        lines.append(f"📅 Upcoming: {len(upcoming)} appointment(s)")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        prog="petcare",
        description="🐾 PetCare Agent — pet sitting, grooming, feeding schedules, vet visits"
    )
    sub = parser.add_subparsers(dest="cmd")

    # add-pet
    p = sub.add_parser("add-pet", help="Register a new pet")
    p.add_argument("--name", required=True, help="Pet name")
    p.add_argument("--species", required=True, help="dog, cat, bird, fish, reptile, other")
    p.add_argument("--breed", default="", help="Breed")
    p.add_argument("--food", default="", help="Food type")
    p.add_argument("--food-amount", default="", help="Amount per feeding")
    p.add_argument("--feeding-times", nargs="+", default=[], help="Feeding times, e.g. 08:00 18:00")
    p.add_argument("--medications", nargs="*", default=[], help="Medications")
    p.add_argument("--vet-name", default="", help="Vet name")
    p.add_argument("--vet-phone", default="", help="Vet phone")
    p.add_argument("--weight-kg", type=float, default=0.0, help="Weight in kg")

    # list-pets
    sub.add_parser("list-pets", help="List all registered pets")

    # remove-pet
    p = sub.add_parser("remove-pet", help="Remove a pet")
    p.add_argument("--name", required=True, help="Pet name")

    # add-appointment
    p = sub.add_parser("add-appointment", help="Schedule an appointment")
    p.add_argument("--pet", required=True, help="Pet name")
    p.add_argument("--type", required=True, help="grooming, vet, boarding, walking, sitting")
    p.add_argument("--date", required=True, help="Date (YYYY-MM-DD)")
    p.add_argument("--time", default="", help="Time (HH:MM)")
    p.add_argument("--location", default="", help="Location")
    p.add_argument("--contact", default="", help="Contact info")
    p.add_argument("--cost", type=float, default=0.0, help="Estimated cost")
    p.add_argument("--notes", default="", help="Notes")

    # list-appointments
    p = sub.add_parser("list-appointments", help="List appointments")
    p.add_argument("--pet", default="", help="Filter by pet name")

    # feeding-schedule
    p = sub.add_parser("feeding-schedule", help="Show feeding schedule")
    p.add_argument("--pet", default="", help="Filter by pet name")

    # report
    sub.add_parser("report", help="Full petcare report")

    args = parser.parse_args()
    agent = PetCareAgent()

    if args.cmd == "add-pet":
        print(agent.add_pet(args.name, args.species,
                            breed=args.breed, food=args.food, food_amount=args.food_amount,
                            feeding_times=args.feeding_times, medications=args.medications,
                            vet_name=args.vet_name, vet_phone=args.vet_phone, weight_kg=args.weight_kg))
    elif args.cmd == "list-pets":
        print(agent.list_pets())
    elif args.cmd == "remove-pet":
        print(agent.remove_pet(args.name))
    elif args.cmd == "add-appointment":
        print(agent.add_appointment(args.pet, args.type, args.date, args.time,
                                    args.location, args.contact, args.cost, args.notes))
    elif args.cmd == "list-appointments":
        print(agent.list_appointments(args.pet))
    elif args.cmd == "feeding-schedule":
        print(agent.feeding_schedule(args.pet))
    elif args.cmd == "report":
        print(agent.care_report())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
