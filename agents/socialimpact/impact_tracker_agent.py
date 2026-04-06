#!/usr/bin/env python3
"""
Impact Tracker Agent - Social Impact Sector
Tracks social impact metrics, outcomes, beneficiaries, and generates impact reports.
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List

LOG_DIR = Path(__file__).parent.parent.parent / "logs" / "socialimpact"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_DIR / "impact_tracker.log"), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ImpactTrackerAgent")


@dataclass
class ImpactMetric:
    id: str; name: str; category: str; unit: str; target: float; current_value: float = 0.0
    description: str = ""; data_source: str = ""; collection_method: str = ""; frequency: str = "monthly"
    created_at: str = ""; updated_at: str = ""

    def __post_init__(self):
        if not self.created_at: self.created_at = datetime.now().isoformat()
        if not self.updated_at: self.updated_at = datetime.now().isoformat()

    @property
    def progress_percentage(self) -> float:
        return min(100.0, (self.current_value / self.target) * 100) if self.target > 0 else 0.0


@dataclass
class Outcome:
    id: str; metric_id: str; value: float; date: str; beneficiary_count: int = 0
    location: str = ""; notes: str = ""; collected_by: str = ""; verified: bool = False


@dataclass
class Beneficiary:
    id: str; name: str; demographic: str = ""; category: str = ""; services_received: List[str] = None
    enrollment_date: str = ""; status: str = "active"; notes: str = ""

    def __post_init__(self):
        if self.services_received is None: self.services_received = []
        if not self.enrollment_date: self.enrollment_date = datetime.now().date().isoformat()


@dataclass
class Program:
    id: str; name: str; description: str = ""; start_date: str = ""; end_date: str = ""
    status: str = "active"; metric_ids: List[str] = None; budget: float = 0.0; spent: float = 0.0
    location: str = ""; target_population: str = ""; outcomes_summary: str = ""

    def __post_init__(self):
        if self.metric_ids is None: self.metric_ids = []
        if not self.start_date: self.start_date = datetime.now().date().isoformat()


class ImpactTracker:
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "data" / "socialimpact"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.data_dir / "impact_metrics.json"
        self.outcomes_file = self.data_dir / "impact_outcomes.json"
        self.beneficiaries_file = self.data_dir / "beneficiaries.json"
        self.programs_file = self.data_dir / "programs.json"
        self.metrics = self._load_json(self.metrics_file, ImpactMetric)
        self.outcomes = self._load_json(self.outcomes_file, Outcome)
        self.beneficiaries = self._load_json(self.beneficiaries_file, Beneficiary)
        self.programs = self._load_json(self.programs_file, Program)

    def _load_json(self, filepath: Path, cls):
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    return {item['id']: cls(**item) for item in data}
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Error loading {filepath}: {e}")
        return {}

    def _save_json(self, filepath: Path, data: dict):
        try:
            with open(filepath, 'w') as f:
                json.dump([asdict(item) for item in data.values()], f, indent=2)
        except IOError as e:
            logger.error(f"Error saving {filepath}: {e}")

    def _save_metrics(self): self._save_json(self.metrics_file, self.metrics)
    def _save_outcomes(self): self._save_json(self.outcomes_file, self.outcomes)
    def _save_beneficiaries(self): self._save_json(self.beneficiaries_file, self.beneficiaries)
    def _save_programs(self): self._save_json(self.programs_file, self.programs)
    def generate_id(self, prefix: str) -> str: return f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def add_metric(self, name: str, category: str, unit: str, target: float,
                   description: str = "", data_source: str = "", collection_method: str = "", frequency: str = "monthly") -> ImpactMetric:
        m = ImpactMetric(id=self.generate_id("metric"), name=name, category=category, unit=unit, target=target,
                         description=description, data_source=data_source, collection_method=collection_method, frequency=frequency)
        self.metrics[m.id] = m; self._save_metrics()
        logger.info(f"Added metric: {name}")
        return m

    def update_metric_value(self, metric_id: str, value: float) -> Optional[ImpactMetric]:
        if metric_id not in self.metrics: return None
        self.metrics[metric_id].current_value = value
        self.metrics[metric_id].updated_at = datetime.now().isoformat()
        self._save_metrics()
        return self.metrics[metric_id]

    def record_outcome(self, metric_id: str, value: float, date: str = None,
                       beneficiary_count: int = 0, location: str = "", notes: str = "", collected_by: str = "") -> Optional[Outcome]:
        if metric_id not in self.metrics: return None
        o = Outcome(id=self.generate_id("out"), metric_id=metric_id, value=value,
                    date=date or datetime.now().date().isoformat(), beneficiary_count=beneficiary_count,
                    location=location, notes=notes, collected_by=collected_by)
        self.outcomes[o.id] = o
        self.metrics[metric_id].current_value += value
        self.metrics[metric_id].updated_at = datetime.now().isoformat()
        self._save_outcomes(); self._save_metrics()
        logger.info(f"Recorded outcome for {metric_id}: {value}")
        return o

    def get_metric(self, metric_id: str) -> Optional[ImpactMetric]: return self.metrics.get(metric_id)
    def list_metrics(self, category: str = None) -> List[ImpactMetric]:
        result = list(self.metrics.values())
        if category: result = [m for m in result if m.category == category]
        result.sort(key=lambda x: x.name.lower())
        return result

    def delete_metric(self, metric_id: str) -> bool:
        if metric_id not in self.metrics: return False
        self.outcomes = {k: v for k, v in self.outcomes.items() if v.metric_id != metric_id}
        del self.metrics[metric_id]
        self._save_metrics(); self._save_outcomes()
        return True

    def add_beneficiary(self, name: str, demographic: str = "", category: str = "", services: List[str] = None, notes: str = "") -> Beneficiary:
        b = Beneficiary(id=self.generate_id("ben"), name=name, demographic=demographic, category=category, services_received=services or [], notes=notes)
        self.beneficiaries[b.id] = b; self._save_beneficiaries()
        logger.info(f"Added beneficiary: {name}")
        return b

    def get_beneficiary(self, beneficiary_id: str) -> Optional[Beneficiary]: return self.beneficiaries.get(beneficiary_id)

    def list_beneficiaries(self, status: str = None, category: str = None) -> List[Beneficiary]:
        result = list(self.beneficiaries.values())
        if status: result = [b for b in result if b.status == status]
        if category: result = [b for b in result if b.category == category]
        return result

    def update_beneficiary(self, beneficiary_id: str, **kwargs) -> Optional[Beneficiary]:
        if beneficiary_id not in self.beneficiaries: return None
        for k, v in kwargs.items():
            if hasattr(self.beneficiaries[beneficiary_id], k): setattr(self.beneficiaries[beneficiary_id], k, v)
        self._save_beneficiaries()
        return self.beneficiaries[beneficiary_id]

    def add_service_to_beneficiary(self, beneficiary_id: str, service: str) -> bool:
        if beneficiary_id not in self.beneficiaries: return False
        if service not in self.beneficiaries[beneficiary_id].services_received:
            self.beneficiaries[beneficiary_id].services_received.append(service)
            self._save_beneficiaries()
        return True

    def graduate_beneficiary(self, beneficiary_id: str) -> bool:
        return bool(self.update_beneficiary(beneficiary_id, status="graduated"))

    def create_program(self, name: str, description: str = "", budget: float = 0.0,
                      location: str = "", target_population: str = "", end_date: str = "") -> Program:
        p = Program(id=self.generate_id("prog"), name=name, description=description, budget=budget,
                    location=location, target_population=target_population, end_date=end_date)
        self.programs[p.id] = p; self._save_programs()
        logger.info(f"Created program: {name}")
        return p

    def link_metric_to_program(self, program_id: str, metric_id: str) -> bool:
        if program_id not in self.programs or metric_id not in self.metrics: return False
        if metric_id not in self.programs[program_id].metric_ids:
            self.programs[program_id].metric_ids.append(metric_id)
            self._save_programs()
        return True

    def update_program_spending(self, program_id: str, amount: float) -> Optional[Program]:
        if program_id not in self.programs: return None
        self.programs[program_id].spent += amount; self._save_programs()
        return self.programs[program_id]

    def get_program(self, program_id: str) -> Optional[Program]: return self.programs.get(program_id)

    def list_programs(self, status: str = None) -> List[Program]:
        result = list(self.programs.values())
        if status: result = [p for p in result if p.status == status]
        return result

    def get_overall_progress(self) -> dict:
        if not self.metrics: return {"total_metrics": 0, "overall_progress": 0}
        total_progress = sum(m.progress_percentage for m in self.metrics.values())
        on_track = len([m for m in self.metrics.values() if m.progress_percentage >= 75])
        at_risk = len([m for m in self.metrics.values() if 50 <= m.progress_percentage < 75])
        behind = len([m for m in self.metrics.values() if m.progress_percentage < 50])
        return {
            "total_metrics": len(self.metrics), "total_beneficiaries": len(self.beneficiaries),
            "active_programs": len([p for p in self.programs.values() if p.status == "active"]),
            "total_outcomes": len(self.outcomes),
            "total_value_delivered": sum(o.value for o in self.outcomes.values()),
            "overall_progress": total_progress / len(self.metrics),
            "on_track": on_track, "at_risk": at_risk, "behind": behind
        }

    def generate_impact_report(self, output_file: Path = None) -> str:
        p = self.get_overall_progress()
        lines = ["=" * 70, "SOCIAL IMPACT REPORT", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", "=" * 70, "",
                 "OVERVIEW", "-" * 50,
                 f"Total Metrics: {p['total_metrics']}", f"Beneficiaries: {p['total_beneficiaries']}",
                 f"Active Programs: {p['active_programs']}", f"Total Outcomes: {p['total_outcomes']}",
                 f"Total Value: {p['total_value_delivered']:.2f}", f"Overall: {p['overall_progress']:.1f}%",
                 f"Status: On Track={p['on_track']} At Risk={p['at_risk']} Behind={p['behind']}"]
        if self.metrics:
            lines.extend(["", "METRICS", "-" * 50])
            for m in self.metrics.values():
                lines.append(f"[{m.progress_percentage:.1f}%] {m.name} | {m.current_value:.0f}/{m.target:.0f} {m.unit} | {m.category}")
        if self.programs:
            lines.extend(["", "PROGRAMS", "-" * 50])
            for pr in self.programs.values():
                lines.append(f"{pr.name} | {pr.status} | Budget: ${pr.budget:,.2f}")
        text = "\n".join(lines)
        if output_file: output_file.write_text(text)
        return text

    def get_category_summary(self) -> dict:
        cats = {}
        for m in self.metrics.values():
            if m.category not in cats: cats[m.category] = {"count": 0, "total_target": 0, "total_current": 0}
            cats[m.category]["count"] += 1; cats[m.category]["total_target"] += m.target; cats[m.category]["total_current"] += m.current_value
        for cat in cats:
            t = cats[cat]["total_target"]
            cats[cat]["progress"] = (cats[cat]["total_current"] / t * 100) if t > 0 else 0
        return cats


def main():
    parser = argparse.ArgumentParser(description="Impact Tracker Agent - Track social impact")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    add_m = subparsers.add_parser("add-metric", help="Add metric")
    add_m.add_argument("--name", required=True); add_m.add_argument("--category", required=True)
    add_m.add_argument("--unit", required=True); add_m.add_argument("--target", type=float, required=True)
    add_m.add_argument("--description", default=""); add_m.add_argument("--data-source", default="")
    add_m.add_argument("--collection-method", default=""); add_m.add_argument("--frequency", default="monthly")

    update_m = subparsers.add_parser("update-metric", help="Update metric value")
    update_m.add_argument("--metric-id", required=True); update_m.add_argument("--value", type=float, required=True)

    record = subparsers.add_parser("record", help="Record outcome")
    record.add_argument("--metric-id", required=True); record.add_argument("--value", type=float, required=True)
    record.add_argument("--date"); record.add_argument("--beneficiaries", type=int, default=0)
    record.add_argument("--location", default=""); record.add_argument("--notes", default=""); record.add_argument("--collected-by", default="")

    list_m = subparsers.add_parser("list-metrics", help="List metrics")
    list_m.add_argument("--category")
    get_m = subparsers.add_parser("get-metric", help="Get metric")
    get_m.add_argument("--metric-id", required=True)
    delete_m = subparsers.add_parser("delete-metric", help="Delete metric")
    delete_m.add_argument("--metric-id", required=True)

    add_b = subparsers.add_parser("add-beneficiary", help="Add beneficiary")
    add_b.add_argument("--name", required=True); add_b.add_argument("--demographic", default="")
    add_b.add_argument("--category", default=""); add_b.add_argument("--services", nargs="*"); add_b.add_argument("--notes", default="")

    list_b = subparsers.add_parser("list-beneficiaries", help="List beneficiaries")
    list_b.add_argument("--status"); list_b.add_argument("--category")
    get_b = subparsers.add_parser("get-beneficiary", help="Get beneficiary")
    get_b.add_argument("--beneficiary-id", required=True)
    subparsers.add_parser("graduate", help="Graduate beneficiary").add_argument("--beneficiary-id", required=True)
    add_service = subparsers.add_parser("add-service", help="Add service")
    add_service.add_argument("--beneficiary-id", required=True); add_service.add_argument("--service", required=True)

    create_p = subparsers.add_parser("create-program", help="Create program")
    create_p.add_argument("--name", required=True); create_p.add_argument("--description", default="")
    create_p.add_argument("--budget", type=float, default=0); create_p.add_argument("--location", default="")
    create_p.add_argument("--target-population", default=""); create_p.add_argument("--end-date", default="")

    link = subparsers.add_parser("link-metric", help="Link metric to program")
    link.add_argument("--program-id", required=True); link.add_argument("--metric-id", required=True)
    spend = subparsers.add_parser("update-spending", help="Update spending")
    spend.add_argument("--program-id", required=True); spend.add_argument("--amount", type=float, required=True)

    list_p = subparsers.add_parser("list-programs", help="List programs")
    list_p.add_argument("--status")
    get_p = subparsers.add_parser("get-program", help="Get program")
    get_p.add_argument("--program-id", required=True)

    subparsers.add_parser("progress", help="Get overall progress")
    subparsers.add_parser("categories", help="Get category summary")
    report = subparsers.add_parser("report", help="Generate report")
    report.add_argument("--output", type=Path)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    tracker = ImpactTracker()
    try:
        if args.command == "add-metric":
            m = tracker.add_metric(args.name, args.category, args.unit, args.target, args.description, args.data_source, args.collection_method, args.frequency)
            print(f"✓ Metric: {m.id} | {m.name} | Target: {m.target} {m.unit}")

        elif args.command == "update-metric":
            m = tracker.update_metric_value(args.metric_id, args.value)
            if m: print(f"✓ {m.current_value}/{m.target} {m.unit} ({m.progress_percentage:.1f}%)")
            else: print("✗ Not found"); sys.exit(1)

        elif args.command == "record":
            o = tracker.record_outcome(args.metric_id, args.value, args.date, args.beneficiaries, args.location, args.notes, args.collected_by)
            if o:
                print(f"✓ Outcome: {o.id}")
            else:
                print("✗ Failed")
                sys.exit(1)

        elif args.command == "list-metrics":
            metrics = tracker.list_metrics(args.category)
            if not metrics: print("No metrics."); return
            print(f"\n{'Name':<35} {'Cat':<12} {'Progress':<18} {'Status'}")
            print("-" * 80)
            for m in metrics:
                pct = m.progress_percentage
                st = "✓" if pct >= 75 else "⚠" if pct >= 50 else "✗"
                print(f"{m.name:<35} {m.category:<12} {m.current_value:.0f}/{m.target:.0f} {m.unit:<6} {pct:>5.1f}% {st}")

        elif args.command == "get-metric":
            m = tracker.get_metric(args.metric_id)
            if not m: print("✗ Not found"); sys.exit(1)
            print(f"\nMETRIC: {m.id}\n{'='*50}\nName: {m.name}\nCategory: {m.category}\nUnit: {m.unit}\nProgress: {m.current_value}/{m.target} ({m.progress_percentage:.1f}%)\nDescription: {m.description or 'N/A'}")

        elif args.command == "delete-metric":
            if tracker.delete_metric(args.metric_id):
                print(f"✓ Deleted")
            else:
                print("✗ Not found")
                sys.exit(1)

        elif args.command == "add-beneficiary":
            b = tracker.add_beneficiary(args.name, args.demographic, args.category, args.services, args.notes)
            print(f"✓ Beneficiary: {b.id} | {b.name}")

        elif args.command == "list-beneficiaries":
            bens = tracker.list_beneficiaries(args.status, args.category)
            if not bens: print("No beneficiaries."); return
            for b in bens: print(f"{b.name} | {b.category} | {b.status} | {len(b.services_received)} services")

        elif args.command == "get-beneficiary":
            b = tracker.get_beneficiary(args.beneficiary_id)
            if not b: print("✗ Not found"); sys.exit(1)
            print(f"\nBENEFICIARY: {b.id}\nName: {b.name}\nCategory: {b.category}\nStatus: {b.status}\nEnrolled: {b.enrollment_date}\nServices: {', '.join(b.services_received) or 'None'}")

        elif args.command == "graduate":
            if tracker.graduate_beneficiary(args.beneficiary_id):
                print(f"✓ Graduated")
            else:
                print("✗ Not found")
                sys.exit(1)

        elif args.command == "add-service":
            if tracker.add_service_to_beneficiary(args.beneficiary_id, args.service):
                print(f"✓ Added")
            else:
                print("✗ Failed")
                sys.exit(1)

        elif args.command == "create-program":
            p = tracker.create_program(args.name, args.description, args.budget, args.location, args.target_population, args.end_date)
            print(f"✓ Program: {p.id} | {p.name}")

        elif args.command == "link-metric":
            if tracker.link_metric_to_program(args.program_id, args.metric_id):
                print(f"✓ Linked")
            else:
                print("✗ Failed")
                sys.exit(1)

        elif args.command == "update-spending":
            p = tracker.update_program_spending(args.program_id, args.amount)
            if p:
                print(f"✓ Spent: ${p.spent:,.2f} / ${p.budget:,.2f}")
            else:
                print("✗ Not found")
                sys.exit(1)

        elif args.command == "list-programs":
            progs = tracker.list_programs(args.status)
            if not progs: print("No programs."); return
            for pr in progs: print(f"{pr.name} | {pr.status} | ${pr.budget:,.2f}")

        elif args.command == "get-program":
            pr = tracker.get_program(args.program_id)
            if not pr: print("✗ Not found"); sys.exit(1)
            print(f"\nPROGRAM: {pr.id}\nName: {pr.name}\nStatus: {pr.status}\nBudget: ${pr.budget:,.2f} | Spent: ${pr.spent:,.2f}\nLocation: {pr.location or 'N/A'}")

        elif args.command == "progress":
            p = tracker.get_overall_progress()
            print(f"\nOVERALL PROGRESS\n{'='*40}\nMetrics: {p['total_metrics']} | Beneficiaries: {p['total_beneficiaries']} | Programs: {p['active_programs']}\nOverall: {p['overall_progress']:.1f}% | On Track: {p['on_track']} | At Risk: {p['at_risk']} | Behind: {p['behind']}")

        elif args.command == "categories":
            cats = tracker.get_category_summary()
            print(f"\nCATEGORIES\n{'='*40}")
            for cat, d in cats.items(): print(f"{cat}: {d['count']} metrics | {d['progress']:.1f}%")

        elif args.command == "report":
            text = tracker.generate_impact_report(args.output)
            if args.output:
                print(f"✓ Saved to {args.output}")
            else:
                print(text)

    except Exception as e:
        logger.exception(f"Error: {e}")
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
