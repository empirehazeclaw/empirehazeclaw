#!/usr/bin/env python3
"""
📊 LLM Analytics Dashboard v1.0
Routing Analytics, Performance Metrics, Cost Analysis
"""

import os, json, argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import *
from collections import defaultdict

class LLMAnalytics:
    def __init__(self):
        self.usage_db = Path("/home/clawbot/.openclaw/workspace/data/llm_usage.json")
        self.cache_db = Path("/home/clawbot/.openclaw/workspace/data/llm_cache.json")
        self.usage_db.parent.mkdir(parents=True, exist_ok=True)
        
        self.usage = self._load_usage()
        self.cache = self._load_cache()
    
    def _load_usage(self) -> dict:
        if self.usage_db.exists():
            return json.loads(self.usage_db.read_text())
        return {"requests": [], "daily_costs": {}, "model_stats": {}}
    
    def _load_cache(self) -> dict:
        if self.cache_db.exists():
            return json.loads(self.cache_db.read_text())
        return {"entries": {}, "stats": {"hits": 0, "misses": 0}}
    
    def get_recent_requests(self, days: int = 7) -> List[dict]:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        return [r for r in self.usage.get("requests", []) if r.get("timestamp", "") >= cutoff]
    
    def get_daily_stats(self, days: int = 7) -> dict:
        daily = defaultdict(lambda: {"requests": 0, "cost": 0, "errors": 0, "latency_sum": 0, "latency_count": 0})
        
        for r in self.get_recent_requests(days):
            date = r["timestamp"][:10]
            daily[date]["requests"] += 1
            daily[date]["cost"] += r.get("cost", 0)
            if not r.get("success", True):
                daily[date]["errors"] += 1
            if r.get("latency"):
                daily[date]["latency_sum"] += r["latency"]
                daily[date]["latency_count"] += 1
        
        return dict(daily)
    
    def get_model_stats(self, days: int = 7) -> dict:
        stats = defaultdict(lambda: {"requests": 0, "success": 0, "errors": 0, "latency_sum": 0, "latency_count": 0, "cost": 0})
        
        for r in self.get_recent_requests(days):
            model = r.get("model", "Unknown")
            stats[model]["requests"] += 1
            if r.get("success", True):
                stats[model]["success"] += 1
            else:
                stats[model]["errors"] += 1
            if r.get("latency"):
                stats[model]["latency_sum"] += r["latency"]
                stats[model]["latency_count"] += 1
            stats[model]["cost"] += r.get("cost", 0)
        
        return dict(stats)
    
    def get_hourly_distribution(self, days: int = 7) -> dict:
        hourly = defaultdict(int)
        for r in self.get_recent_requests(days):
            hour = int(r["timestamp"][11:13])
            hourly[hour] += 1
        return dict(hourly)
    
    def get_provider_stats(self, days: int = 7) -> dict:
        providers = defaultdict(lambda: {"requests": 0, "cost": 0, "success_rate": 0})
        
        for r in self.get_recent_requests(days):
            provider = r.get("provider", "Unknown")
            providers[provider]["requests"] += 1
            providers[provider]["cost"] += r.get("cost", 0)
        
        # Calculate success rates
        model_stats = self.get_model_stats(days)
        for provider, data in providers.items():
            provider_models = [m for m, s in model_stats.items() if provider.lower() in m.lower() or provider in ["Google", "OpenAI", "Anthropic", "OpenRouter"]]
            total_success = sum(model_stats.get(m, {}).get("success", 0) for m in provider_models)
            total_requests = sum(model_stats.get(m, {}).get("requests", 0) for m in provider_models)
            data["success_rate"] = total_success / max(total_requests, 1) * 100
        
        return dict(providers)
    
    def calculate_sla(self, days: int = 7) -> dict:
        requests = self.get_recent_requests(days)
        if not requests:
            return {"uptime": 100, "total_requests": 0, "successful": 0, "failed": 0}
        
        successful = sum(1 for r in requests if r.get("success", True))
        failed = sum(1 for r in requests if not r.get("success", True))
        uptime = successful / len(requests) * 100
        
        avg_latency = sum(r.get("latency", 0) for r in requests if r.get("latency")) / max(sum(1 for r in requests if r.get("latency")), 1)
        
        return {
            "uptime": uptime,
            "total_requests": len(requests),
            "successful": successful,
            "failed": failed,
            "avg_latency_ms": avg_latency
        }
    
    def get_cache_performance(self) -> dict:
        cache_stats = self.cache.get("stats", {})
        entries = self.cache.get("entries", {})
        
        hits = cache_stats.get("hits", 0)
        misses = cache_stats.get("misses", 0)
        total = hits + misses
        
        # Calculate expired entries
        now = time.time()
        expired = sum(1 for e in entries.values() if now - e.get("timestamp", 0) > 3600)
        
        return {
            "hits": hits,
            "misses": misses,
            "hit_rate": hits / max(total, 1) * 100,
            "total_requests": total,
            "cached_entries": len(entries),
            "expired_entries": expired,
            "active_entries": len(entries) - expired
        }
    
    def generate_report(self, days: int = 7) -> str:
        daily = self.get_daily_stats(days)
        model_stats = self.get_model_stats(days)
        provider_stats = self.get_provider_stats(days)
        sla = self.calculate_sla(days)
        cache_perf = self.get_cache_performance()
        hourly = self.get_hourly_distribution(days)
        
        # Calculate totals
        total_cost = sum(d.get("cost", 0) for d in daily.values())
        total_requests = sum(d.get("requests", 0) for d in daily.values())
        total_errors = sum(d.get("errors", 0) for d in daily.values())
        
        # Best performing model
        best_model = max(model_stats.items(), key=lambda x: x[1].get("success", 0) / max(x[1].get("requests", 1), 1), default=(None, {}))
        
        # Peak hour
        peak_hour = max(hourly.items(), key=lambda x: x[1], default=(0, 0))
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    📊 LLM ANALYTICS DASHBOARD                             ║
║                         Report: Last {days} Days                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  ┌─ OVERALL METRICS ─────────────────────────────────────────────────────┐ ║
║  │                                                                     │ ║
║  │  💰 Total Cost:           ${total_cost:.6f}                             │ ║
║  │  📊 Total Requests:       {total_requests:>6}                             │ ║
║  │  ⚠️  Total Errors:         {total_errors:>6}                             │ ║
║  │  ✅ Success Rate:           {sla['uptime']:>6.1f}%                             │ ║
║  │  ⚡ Avg Latency:           {sla['avg_latency_ms']:>6.0f}ms                            │ ║
║  │                                                                     │ ║
║  └─────────────────────────────────────────────────────────────────────┘ ║
║                                                                           ║
║  ┌─ PROVIDER BREAKDOWN ──────────────────────────────────────────────────┐ ║"""
        
        for provider, data in sorted(provider_stats.items(), key=lambda x: x[1]["requests"], reverse=True)[:4]:
            sr = data.get("success_rate", 0)
            report += f"\n║  │  {provider:15} | {data['requests']:>4} req | {sr:>5.1f}% success | ${data['cost']:.4f}       │ ║"
        
        report += f"""
║  └─────────────────────────────────────────────────────────────────────┘ ║
║                                                                           ║
║  ┌─ TOP MODELS ─────────────────────────────────────────────────────────┐ ║"""
        
        for model, data in sorted(model_stats.items(), key=lambda x: x[1].get("requests", 0), reverse=True)[:5]:
            sr = data.get("success", 0) / max(data.get("requests", 1), 1) * 100
            avg_lat = data.get("latency_sum", 0) / max(data.get("latency_count", 1), 1)
            report += f"\n║  │  {model:20} | {data['requests']:>4} req | {sr:>5.1f}% | {avg_lat:>6.0f}ms      │ ║"
        
        report += f"""
║  └─────────────────────────────────────────────────────────────────────┘ ║
║                                                                           ║
║  ┌─ CACHE PERFORMANCE ─────────────────────────────────────────────────┐ ║
║  │                                                                     │ ║
║  │  📦 Cache Hit Rate:      {cache_perf['hit_rate']:>6.1f}%                             │ ║
║  │  ✅ Hits:                {cache_perf['hits']:>6}                             │ ║
║  │  ❌ Misses:              {cache_perf['misses']:>6}                             │ ║
║  │  📁 Active Entries:       {cache_perf['active_entries']:>6}                             │ ║
║  │                                                                     │ ║
║  └─────────────────────────────────────────────────────────────────────┘ ║
║                                                                           ║
║  ┌─ DAILY BREAKDOWN ───────────────────────────────────────────────────┐ ║"""
        
        for date, data in sorted(daily.items(), reverse=True)[:7]:
            sr = (data["requests"] - data["errors"]) / max(data["requests"], 1) * 100
            avg_lat = data["latency_sum"] / max(data["latency_count"], 1)
            report += f"\n║  │  {date} | {data['requests']:>4} req | {sr:>5.1f}% | {avg_lat:>6.0f}ms | ${data['cost']:.4f}   │ ║"
        
        report += f"""
║  └─────────────────────────────────────────────────────────────────────┘ ║
║                                                                           ║
║  ┌─ PEAK USAGE ────────────────────────────────────────────────────────┐ ║
║  │                                                                     │ ║
║  │  🕐 Peak Hour:           {peak_hour[0]:>02d}:00 - {(peak_hour[0]+1)%24:>02d}:00 ({peak_hour[1]} requests)              │ ║
║  │                                                                     │ ║
║  └─────────────────────────────────────────────────────────────────────┘ ║
║                                                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return report


if __name__ == "__main__":
    import time
    import urllib.request
    
    parser = argparse.ArgumentParser(description="LLM Analytics Dashboard")
    parser.add_argument("--days", "-d", type=int, default=7, help="Days to analyze")
    parser.add_argument("--report", "-r", action="store_true", help="Full report")
    parser.add_argument("--export", "-e", help="Export to JSON file")
    args = parser.parse_args()
    
    analytics = LLMAnalytics()
    
    if args.export:
        data = {
            "daily": analytics.get_daily_stats(args.days),
            "models": analytics.get_model_stats(args.days),
            "providers": analytics.get_provider_stats(args.days),
            "sla": analytics.calculate_sla(args.days),
            "cache": analytics.get_cache_performance(),
            "hourly": analytics.get_hourly_distribution(args.days)
        }
        Path(args.export).write_text(json.dumps(data, indent=2))
        print(f"Exported to {args.export}")
    else:
        print(analytics.generate_report(args.days))
