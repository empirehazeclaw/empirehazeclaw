#!/usr/bin/env python3
"""
Logistics Optimizer Agent
==========================
Route optimisation (nearest-neighbour + 2-opt TSP), load planning,
carrier selection, delivery window validation, and cost estimation.
Supports multi-stop shipments and real-time cost breakdowns.

Usage:
    python3 logistics_optimizer_agent.py --route data/stops.json
    python3 logistics_optimizer_agent.py --simulate
    python3 logistics_optimizer_agent.py --shipment data/shipment.json
    python3 logistics_optimizer_agent.py --cost-compare
"""

import argparse
import json
import logging
import math
import os
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("LogisticsOptimizer")


# ── Data Models ───────────────────────────────────────────────────────────────
@dataclass
class Stop:
    id: str
    name: str
    lat: float
    lng: float
    address: str = ""
    time_window_start: str = "08:00"   # HH:MM
    time_window_end: str = "18:00"
    service_time_minutes: int = 15
    priority: int = 1                  # 1=highest


@dataclass
class Shipment:
    shipment_id: str
    origin_id: str
    destination_ids: list[str]
    items: list[dict]     # [{"sku": "...", "qty": int, "weight_kg": float, "volume_m3": float}]
    pickup_date: str
    delivery_date: str
    carrier: str = "auto"
    status: str = "planned"


@dataclass
class Route:
    route_id: str
    stops: list[Stop]
    total_distance_km: float
    total_time_hours: float
    cost_eur: float
    carrier: str
    co2_kg: float
    sequence: list[str]


@dataclass
class CarrierRate:
    carrier: str
    service: str            # express | standard | economy
    rate_per_kg: float
    rate_per_km: float
    base_rate: float        # fixed pickup charge
    max_weight_kg: float
    max_volume_m3: float
    transit_days: int
    tracking_included: bool = True


# ── Data Store ───────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "supply_chain")
STOPS_FILE = os.path.join(DATA_DIR, "logistics_stops.json")
ROUTES_FILE = os.path.join(DATA_DIR, "optimized_routes.json")
SHIPMENTS_FILE = os.path.join(DATA_DIR, "logistics_shipments.json")
CARRIERS_FILE = os.path.join(DATA_DIR, "carrier_rates.json")


def load_json(path, default=None):
    if default is None:
        default = []
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            log.warning("Could not load %s: %s", path, e)
    return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ── Geographic Helpers ────────────────────────────────────────────────────────
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two lat/lng points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + (
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def road_distance(haversine_km: float) -> float:
    """Apply road factor (≈1.35× straight-line for Europe)."""
    return haversine_km * 1.35


# ── Core Logic ────────────────────────────────────────────────────────────────
class LogisticsOptimizer:
    # Average fuel consumption L/100km and CO2 kg/L for a 16t truck
    FUEL_L_PER_100KM = 24.0
    CO2_KG_PER_L = 2.64

    def __init__(self):
        self.stops: list[Stop] = []
        self.routes: list[Route] = []
        self.shipments: list[Shipment] = []
        self.carriers: list[CarrierRate] = []

    # ── Data Loading ───────────────────────────────────────────────────────────
    def load_stops(self, path: Optional[str] = None):
        path = path or STOPS_FILE
        raw = load_json(path, [])
        self.stops = [Stop(**s) if isinstance(s, dict) else s for s in raw]
        log.info("Loaded %d logistics stops", len(self.stops))

    def load_carriers(self, path: Optional[str] = None):
        path = path or CARRIERS_FILE
        raw = load_json(path, [])
        self.carriers = [CarrierRate(**c) if isinstance(c, dict) else c for c in raw]
        log.info("Loaded %d carrier rate tables", len(self.carriers))

    def load_shipments(self, path: Optional[str] = None):
        path = path or SHIPMENTS_FILE
        raw = load_json(path, [])
        self.shipments = [Shipment(**s) if isinstance(s, dict) else s for s in raw]
        log.info("Loaded %d shipments", len(self.shipments))

    def generate_sample_data(self):
        import random
        random.seed(99)
        # European logistics stops
        stop_data = [
            ("DEP-01", "Warehouse Berlin", 52.52, 13.405, "Berlin, Germany"),
            ("CUST-01", "Retail Frankfurt", 50.1109, 8.6821, "Frankfurt, Germany"),
            ("CUST-02", "Factory Munich", 48.1351, 11.5820, "Munich, Germany"),
            ("CUST-03", "Warehouse Hamburg", 53.5511, 9.9937, "Hamburg, Germany"),
            ("CUST-04", "DC Cologne", 50.9375, 6.9603, "Cologne, Germany"),
            ("CUST-05", "Store Stuttgart", 48.7758, 9.1829, "Stuttgart, Germany"),
            ("CUST-06", "Partner Leipzig", 51.3397, 12.3731, "Leipzig, Germany"),
            ("CUST-07", "Hub Hanover", 52.3759, 9.7320, "Hanover, Germany"),
            ("CUST-08", "Retail Dresden", 51.0504, 13.7373, "Dresden, Germany"),
            ("RET-01", "Returns Centre", 48.3736, 10.8945, "Augsburg, Germany"),
        ]
        time_windows = [
            ("07:00", "12:00"), ("09:00", "17:00"), ("08:00", "14:00"),
            ("10:00", "18:00"), ("08:00", "16:00"), ("07:30", "13:00"),
            ("09:00", "18:00"), ("08:00", "15:00"), ("10:00", "17:00"),
            ("08:00", "12:00"),
        ]
        self.stops = [
            Stop(
                id=sid, name=name, lat=lat, lng=lng, address=addr,
                time_window_start=tw[0], time_window_end=tw[1],
                service_time_minutes=random.randint(10, 30),
                priority=random.randint(1, 3),
            )
            for (sid, name, lat, lng, addr), tw in zip(stop_data, time_windows)
        ]
        log.info("Generated %d sample stops", len(self.stops))
        self._save_stops()

        # Carrier rates
        self.carriers = [
            CarrierRate(carrier="DHL Express", service="express",
                        rate_per_kg=1.80, rate_per_km=0.45, base_rate=25.0,
                        max_weight_kg=70, max_volume_m3=0.4,
                        transit_days=1, tracking_included=True),
            CarrierRate(carrier="DHL Freight", service="standard",
                        rate_per_kg=0.45, rate_per_km=0.22, base_rate=40.0,
                        max_weight_kg=5000, max_volume_m3=80,
                        transit_days=3, tracking_included=True),
            CarrierRate(carrier="DB Schenker", service="standard",
                        rate_per_kg=0.38, rate_per_km=0.18, base_rate=35.0,
                        max_weight_kg=8000, max_volume_m3=120,
                        transit_days=4, tracking_included=True),
            CarrierRate(carrier="Dachser", service="economy",
                        rate_per_kg=0.28, rate_per_km=0.14, base_rate=30.0,
                        max_weight_kg=10000, max_volume_m3=150,
                        transit_days=5, tracking_included=True),
            CarrierRate(carrier="UPS", service="express",
                        rate_per_kg=2.10, rate_per_km=0.50, base_rate=20.0,
                        max_weight_kg=50, max_volume_m3=0.3,
                        transit_days=1, tracking_included=True),
        ]
        self._save_carriers()

        # Sample shipments
        self.shipments = [
            Shipment(
                shipment_id="SHP-7001",
                origin_id="DEP-01",
                destination_ids=["CUST-01", "CUST-02"],
                items=[{"sku": "SKU-101", "qty": 200, "weight_kg": 400.0, "volume_m3": 2.0}],
                pickup_date=datetime.utcnow().strftime("%Y-%m-%d"),
                delivery_date=(datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d"),
            ),
            Shipment(
                shipment_id="SHP-7002",
                origin_id="DEP-01",
                destination_ids=["CUST-03", "CUST-04", "CUST-05"],
                items=[{"sku": "SKU-102", "qty": 80, "weight_kg": 120.0, "volume_m3": 1.5}],
                pickup_date=datetime.utcnow().strftime("%Y-%m-%d"),
                delivery_date=(datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d"),
            ),
        ]
        self._save_shipments()

    # ── Persistence ────────────────────────────────────────────────────────────
    def _save_stops(self):
        save_json(STOPS_FILE, [s.__dict__ for s in self.stops])

    def _save_carriers(self):
        save_json(CARRIERS_FILE, [c.__dict__ for c in self.carriers])

    def _save_shipments(self):
        save_json(SHIPMENTS_FILE, [s.__dict__ for s in self.shipments])

    # ── Route Optimisation ──────────────────────────────────────────────────────
    def nearest_neighbour_tsp(self, start_idx: int) -> list[int]:
        """Nearest-neighbour heuristic for TSP."""
        n = len(self.stops)
        visited = [False] * n
        route = [start_idx]
        visited[start_idx] = True
        current = start_idx
        for _ in range(n - 1):
            best = None
            best_dist = float("inf")
            for j in range(n):
                if visited[j]:
                    continue
                d = road_distance(haversine_km(
                    self.stops[current].lat, self.stops[current].lng,
                    self.stops[j].lat, self.stops[j].lng
                ))
                if d < best_dist:
                    best_dist = d
                    best = j
            if best is not None:
                route.append(best)
                visited[best] = True
                current = best
        return route

    def two_opt_improve(self, route: list[int]) -> list[int]:
        """2-opt local search to improve TSP route."""
        improved = True
        best_route = route[:]
        n = len(best_route)
        while improved:
            improved = False
            for i in range(1, n - 2):
                for j in range(i + 1, n):
                    if j - i == 1:
                        continue
                    # Reverse segment between i and j
                    new_route = best_route[:i] + best_route[i:j][::-1] + best_route[j:]
                    if self._route_distance(new_route) < self._route_distance(best_route):
                        best_route = new_route
                        improved = True
        return best_route

    def _route_distance(self, route: list[int]) -> float:
        total = 0.0
        for k in range(len(route) - 1):
            total += road_distance(haversine_km(
                self.stops[route[k]].lat, self.stops[route[k]].lng,
                self.stops[route[k + 1]].lat, self.stops[route[k + 1]].lng
            ))
        return total

    def optimize_route(
        self,
        origin_id: str,
        destination_ids: list[str],
        carrier: str = "DHL Freight",
        departure_time: Optional[datetime] = None,
    ) -> Route:
        """Build and optimise a multi-stop delivery route."""
        # Collect indices into self.stops for origin and destinations
        origin_idxs = [i for i, s in enumerate(self.stops) if s.id == origin_id]
        dest_idxs = [i for i, s in enumerate(self.stops) if s.id in destination_ids]
        all_idxs = origin_idxs + dest_idxs

        if not all_idxs:
            raise ValueError(f"Stops not found for route {origin_id} → {destination_ids}")

        if len(origin_idxs) == 0:
            raise ValueError(f"Origin stop '{origin_id}' not found in stop list")

        # Build a mini working list of Stop objects in the order of all_idxs
        working_stops = [self.stops[i] for i in all_idxs]

        # Temporarily override self.stops with the subset so TSP helpers work
        saved_stops = self.stops
        self.stops = working_stops
        try:
            # TSP optimisation: start from position 0 (origin)
            nn_route = self.nearest_neighbour_tsp(0)
            opt_route = self.two_opt_improve(nn_route)

            # opt_route contains indices into working_stops → map back to original indices
            stop_indices = [all_idxs[i] for i in opt_route]
        finally:
            self.stops = saved_stops

        # Calculate metrics
        total_dist = self._route_distance(stop_indices)
        # Service time
        service_hours = sum(
            self.stops[i].service_time_minutes / 60.0 for i in stop_indices
        )
        avg_speed_kmh = 65.0   # urban/mixed average
        drive_hours = total_dist / avg_speed_kmh
        total_hours = drive_hours + service_hours

        # CO2
        co2 = (total_dist / 100.0) * self.FUEL_L_PER_100KM * self.CO2_KG_PER_L

        # Cost
        carrier_rate = next((c for c in self.carriers if c.carrier == carrier), None)
        if carrier_rate:
            # Estimate total weight/volume from shipments (use defaults)
            est_weight_kg = 1000.0
            cost = (carrier_rate.base_rate +
                    carrier_rate.rate_per_kg * est_weight_kg +
                    carrier_rate.rate_per_km * total_dist)
        else:
            cost = 15.0 + 0.30 * total_dist  # fallback

        seq = [self.stops[i].id for i in stop_indices]
        route = Route(
            route_id=f"RT-{datetime.utcnow().strftime('%m%d%H%M')}",
            stops=[self.stops[i] for i in stop_indices],
            total_distance_km=round(total_dist, 1),
            total_time_hours=round(total_hours, 2),
            cost_eur=round(cost, 2),
            carrier=carrier,
            co2_kg=round(co2, 1),
            sequence=seq,
        )
        self.routes.append(route)
        self._save_routes()
        log.info(
            "Optimised route %s: %s (%.1f km, %.2fh, %.2f EUR, %.1f kg CO2)",
            route.route_id, "→".join(seq),
            route.total_distance_km, route.total_time_hours,
            route.cost_eur, route.co2_kg,
        )
        return route

    def _save_routes(self):
        data = [
            {
                **r.__dict__,
                "stops": [s.__dict__ for s in r.stops],
            }
            for r in self.routes
        ]
        save_json(ROUTES_FILE, data)

    # ── Load Planning ───────────────────────────────────────────────────────────
    def plan_load(self, shipment: Shipment) -> dict:
        """Check weight/volume capacity and generate load plan."""
        total_weight = sum(item.get("weight_kg", 0) for item in shipment.items)
        total_volume = sum(item.get("volume_m3", 0) for item in shipment.items)

        # Standard European pallet: 1.2×0.8m, height 2.0m → 1.92 m3, max 1500 kg
        pallet_limit_kg = 1500.0
        pallet_limit_vol = 1.92
        num_pallets = max(1, int(math.ceil(
            max(total_weight / pallet_limit_kg, total_volume / pallet_limit_vol)
        )))
        avg_weight_per_pallet = total_weight / num_pallets
        avg_vol_per_pallet = total_volume / num_pallets

        capacity_util = min(
            total_weight / (num_pallets * pallet_limit_kg),
            total_volume / (num_pallets * pallet_limit_vol),
        ) * 100

        return {
            "shipment_id": shipment.shipment_id,
            "total_weight_kg": round(total_weight, 2),
            "total_volume_m3": round(total_volume, 2),
            "pallets_required": num_pallets,
            "avg_weight_per_pallet_kg": round(avg_weight_per_pallet, 1),
            "avg_volume_per_pallet_m3": round(avg_vol_per_pallet, 3),
            "capacity_utilization_pct": round(capacity_util, 1),
            "warnings": (
                ["⚠️ Overweight per pallet"] if avg_weight_per_pallet > pallet_limit_kg else []
            ),
        }

    # ── Carrier Selection ─────────────────────────────────────────────────────
    def select_carrier(self, shipment: Shipment) -> list[dict]:
        """Rank carriers by total cost for a given shipment."""
        total_weight = sum(item.get("weight_kg", 0) for item in shipment.items)
        total_volume = sum(item.get("volume_m3", 0) for item in shipment.items)
        # Estimate distance from origin/destination stops
        origin = next((s for s in self.stops if s.id == shipment.origin_id), None)
        dests = [s for s in self.stops if s.id in shipment.destination_ids]
        if origin and dests:
            dists = [
                road_distance(haversine_km(origin.lat, origin.lng, d.lat, d.lng))
                for d in dests
            ]
            avg_dist = sum(dists) / len(dists) * 1.5  # multi-stop factor
        else:
            avg_dist = 500.0  # default assumption

        results = []
        for c in self.carriers:
            if total_weight > c.max_weight_kg or total_volume > c.max_volume_m3:
                continue
            cost = c.base_rate + c.rate_per_kg * total_weight + c.rate_per_km * avg_dist
            results.append({
                "carrier": c.carrier,
                "service": c.service,
                "transit_days": c.transit_days,
                "cost_eur": round(cost, 2),
                "cost_per_kg": round(cost / total_weight, 4) if total_weight > 0 else 0,
                "tracking": c.tracking_included,
                "rating": "★★★★★" if c.transit_days == 1 else
                          "★★★★" if c.transit_days <= 2 else
                          "★★★" if c.transit_days <= 4 else "★★",
            })
        return sorted(results, key=lambda x: x["cost_eur"])

    # ── Delivery Window Validation ────────────────────────────────────────────
    def validate_time_windows(self, route: Route,
                               departure: datetime) -> dict:
        """Check if route respects all stop time windows."""
        warnings = []
        current_time = departure
        avg_speed_kmh = 65.0

        for stop in route.stops:
            # Distance from previous stop
            prev = route.stops[route.stops.index(stop) - 1] if route.stops.index(stop) > 0 else None
            if prev:
                dist = road_distance(haversine_km(prev.lat, prev.lng, stop.lat, stop.lng))
                travel_min = dist / avg_speed_kmh * 60
                current_time += timedelta(minutes=travel_min)

            # Parse time window
            try:
                tw_start = datetime.strptime(stop.time_window_start, "%H:%M").time()
                tw_end = datetime.strptime(stop.time_window_end, "%H:%M").time()
                cur_time_of_day = current_time.time()

                if cur_time_of_day > tw_end:
                    warnings.append(
                        f"⚠ {stop.id} ({stop.name}): Arrival {cur_time_of_day.strftime('%H:%M')} "
                        f"AFTER window close {stop.time_window_end}"
                    )
                elif cur_time_of_day < tw_start:
                    # Wait until window opens
                    wait_min = (
                        datetime.combine(current_time.date(), tw_start) - current_time
                    ).total_seconds() / 60
                    warnings.append(
                        f"ℹ {stop.id} ({stop.name}): Early arrival — waiting {int(wait_min)} min"
                    )
            except ValueError:
                pass

            # Add service time
            current_time += timedelta(minutes=stop.service_time_minutes)

        return {
            "route_id": route.route_id,
            "departure": departure.isoformat(),
            "estimated_finish": current_time.isoformat(),
            "total_travel_minutes": int((current_time - departure).total_seconds() / 60),
            "warnings": warnings,
            "all_windows_met": len([w for w in warnings if w.startswith("⚠")]) == 0,
        }

    # ── Print Methods ───────────────────────────────────────────────────────────
    def print_route(self, route: Route):
        print(f"\n🚚 OPTIMISED ROUTE — {route.route_id} ─────────────────────────────────────")
        print(f"  Carrier : {route.carrier}")
        print(f"  Distance: {route.total_distance_km:.1f} km")
        print(f"  Duration: {route.total_time_hours:.2f} h")
        print(f"  Cost    : €{route.cost_eur:.2f}")
        print(f"  CO₂     : {route.co2_kg:.1f} kg")
        print()
        print(f"  {'Seq':<4} {'Stop ID':<10} {'Name':<22} {'TW':>11} {'Svc min':>8}")
        print("  " + "-" * 60)
        for i, stop in enumerate(route.stops, 1):
            print(
                f"  {i:<4} {stop.id:<10} {stop.name:<22} "
                f"{stop.time_window_start}-{stop.time_window_end:>11} "
                f"{stop.service_time_minutes:>8}"
            )
        print("  " + "-" * 60)

    def print_carrier_comparison(self, shipment: Shipment):
        options = self.select_carrier(shipment)
        if not options:
            print(f"\n⚠ No eligible carriers for shipment {shipment.shipment_id}")
            return
        load = self.plan_load(shipment)
        print(f"\n📦 SHIPMENT {shipment.shipment_id} LOAD PLAN ──────────────────────────────")
        print(f"  Total weight  : {load['total_weight_kg']:.1f} kg")
        print(f"  Total volume  : {load['total_volume_m3']:.3f} m³")
        print(f"  Pallets needed: {load['pallets_required']} "
              f"(util: {load['capacity_utilization_pct']:.1f}%)")
        for w in load.get("warnings", []):
            print(f"  {w}")

        print(f"\n🚛 CARRIER OPTIONS ───────────────────────────────────────────────────")
        print(f"  {'Carrier':<18} {'Service':<10} {'Transit':>8} {'Cost':>10} "
              f"{'€/kg':>8} {'Rating':<6} {'Tracking'}")
        print("  " + "-" * 72)
        for opt in options:
            trk = "✅" if opt["tracking"] else "❌"
            print(
                f"  {opt['carrier']:<18} {opt['service']:<10} "
                f"{opt['transit_days']:>7}d €{opt['cost_eur']:>8.2f} "
                f"{opt['cost_per_kg']:>7.4f} {opt['rating']:<6} {trk}"
            )

    def print_routes(self):
        if not self.routes:
            print("No routes optimised yet.")
            return
        print("\n📋 SAVED ROUTES ──────────────────────────────────────────────────────")
        print(f"  {'Route ID':<12} {'Carrier':<18} {'Distance':>10} {'Duration':>10} "
              f"{'Cost':>10} {'CO₂ kg':>10}")
        print("  " + "-" * 72)
        for r in self.routes:
            print(
                f"  {r.route_id:<12} {r.carrier:<18} {r.total_distance_km:>9.1f}km "
                f"{r.total_time_hours:>9.2f}h €{r.cost_eur:>9.2f} {r.co2_kg:>10.1f}"
            )


# ── CLI ───────────────────────────────────────────────────────────────────────
def build_parser():
    parser = argparse.ArgumentParser(
        prog="logistics_optimizer_agent.py",
        description="Logistics Optimizer — route planning, carrier selection, load planning.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --simulate                 Generate sample stops + carriers
  %(prog)s --route data/stops.json   Optimise route for stop file
  %(prog)s --shipment data/shipment.json --plan-load
  %(prog)s --cost-compare            Compare carrier rates
  %(prog)s --routes                  List saved routes
  %(prog)s --validate                Validate time windows on last route
        """,
    )
    parser.add_argument("--route", dest="route_file",
                        metavar="ROUTE_FILE", nargs="?", const="__use_origin__",
                        help="Optimise route for given stop-file (or use --origin/--dests if no file)")
    parser.add_argument("--origin", dest="origin_id",
                        help="Origin stop ID (required with --route)")
    parser.add_argument("--dests", dest="dest_ids", nargs="+",
                        help="Destination stop IDs")
    parser.add_argument("--carrier", default="DHL Freight",
                        help="Carrier name")
    parser.add_argument("--shipment", dest="shipment_file",
                        help="JSON file describing shipment")
    parser.add_argument("--plan-load", action="store_true",
                        help="Print load planning for shipment")
    parser.add_argument("--cost-compare", action="store_true",
                        dest="cost_compare",
                        help="Compare carrier rates for shipment")
    parser.add_argument("--routes", action="store_true",
                        help="List all saved routes")
    parser.add_argument("--validate", action="store_true",
                        help="Validate time windows for last route")
    parser.add_argument("--simulate", action="store_true",
                        help="Generate sample logistics data")
    parser.add_argument("--stops-file", dest="stops_file",
                        help="Path to stops JSON")
    parser.add_argument("--verbose", "-v", action="store_true")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    opt = LogisticsOptimizer()

    try:
        if args.simulate:
            opt.generate_sample_data()
        else:
            opt.load_stops(args.stops_file)
            opt.load_carriers()
            opt.load_shipments()

        if args.routes:
            opt.print_routes()
            return

        if args.cost_compare:
            if not opt.shipments:
                opt.load_shipments()
            for sh in opt.shipments:
                opt.print_carrier_comparison(sh)
            return

        if getattr(args, "shipment_file", None):
            import json as _json
            try:
                raw = _json.load(open(args.shipment_file))
            except Exception:
                raw = [{"shipment_id": "SHP-CLI", "origin_id": "DEP-01",
                        "destination_ids": ["CUST-01", "CUST-02"],
                        "items": [{"sku": "SKU-001", "qty": 100,
                                   "weight_kg": 200.0, "volume_m3": 1.0}],
                        "pickup_date": datetime.utcnow().strftime("%Y-%m-%d"),
                        "delivery_date": (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d")}]
            for sh_data in raw:
                sh = Shipment(**sh_data)
                if args.plan_load:
                    load = opt.plan_load(sh)
                    print(f"\n📦 Load Plan for {sh.shipment_id}:")
                    for k, v in load.items():
                        print(f"  {k}: {v}")
                opt.print_carrier_comparison(sh)
            return

        if getattr(args, "route_file", None):
            if not args.origin_id:
                parser.error("--origin required with --route")
            if not args.dest_ids:
                parser.error("--dests required with --route")
            # Load stops from file if provided (not just __use_origin__)
            if args.route_file and args.route_file != "__use_origin__" and os.path.exists(args.route_file):
                raw = load_json(args.route_file, [])
                opt.stops = [Stop(**s) if isinstance(s, dict) else s for s in raw]
            route = opt.optimize_route(args.origin_id, args.dest_ids, carrier=args.carrier)
            opt.print_route(route)

            # Time window validation
            departure = datetime.utcnow().replace(hour=7, minute=0, second=0, microsecond=0)
            v = opt.validate_time_windows(route, departure)
            print(f"\n⏰ TIME WINDOW VALIDATION ────────────────────────────────────────────")
            print(f"  Departure : {v['departure']}")
            print(f"  Est. finish: {v['estimated_finish']}")
            print(f"  Total time : {v['total_travel_minutes']} min")
            if v["warnings"]:
                for w in v["warnings"]:
                    print(f"  {w}")
            else:
                print("  ✅ All time windows satisfied.")
            return

        # Default: show summary
        opt.print_routes()
        if opt.stops:
            print(f"\nℹ {len(opt.stops)} stops loaded. Use --route to optimise a route.")

    except KeyboardInterrupt:
        log.info("Interrupted.")
        sys.exit(130)
    except ValueError as e:
        log.error("%s", e)
        sys.exit(1)
    except Exception as e:
        log.exception("Fatal error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
