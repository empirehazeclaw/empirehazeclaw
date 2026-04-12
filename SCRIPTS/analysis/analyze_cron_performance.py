#!/usr/bin/env python3
"""
Cron Performance Analyzer
Analyzes cron job outcomes and learns patterns
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

CRON_DB = "/home/clawbot/.openclaw/cron-automation/cron.db"

class CronAnalyzer:
    def __init__(self):
        self.analysis_file = "/home/clawbot/.openclaw/workspace/memory/cron_analysis.json"
        self.load_analysis()
        
    def load_analysis(self):
        if os.path.exists(self.analysis_file):
            with open(self.analysis_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "job_performance": {},  # job_id -> success_rate
                "time_performance": {}, # hour -> success_rate
                "day_performance": {}, # day -> success_rate
                "last_analysis": None
            }
            
    def save_analysis(self):
        with open(self.analysis_file, 'w') as f:
            json.dump(self.data, f, indent=2)
            
    def analyze_cron_jobs(self):
        """Analyze cron job performance from database"""
        if not os.path.exists(CRON_DB):
            return None
            
        # Read cron database (SQLite)
        import sqlite3
        conn = sqlite3.connect(CRON_DB)
        cursor = conn.cursor()
        
        # Get recent runs
        cursor.execute("""
            SELECT job_name, status, start_time 
            FROM cron_runs 
            WHERE start_time > datetime('now', '-7 days')
            ORDER BY start_time DESC
            LIMIT 100
        """)
        
        runs = cursor.fetchall()
        conn.close()
        
        if not runs:
            return None
            
        # Analyze by job
        job_stats = defaultdict(lambda: {"success": 0, "failed": 0, "total": 0})
        time_stats = defaultdict(lambda: {"success": 0, "failed": 0, "total": 0})
        day_stats = defaultdict(lambda: {"success": 0, "failed": 0, "total": 0})
        
        for run in runs:
            job_name, status, started_at = run
            
            # Parse time
            try:
                dt = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                hour = dt.hour
                day = dt.weekday()
            except:
                # Try different format
                try:
                    dt = datetime.strptime(started_at[:19], '%Y-%m-%d %H:%M:%S')
                    hour = dt.hour
                    day = dt.weekday()
                except:
                    continue
                
            # Job stats
            job_stats[job_name]["total"] += 1
            if status == "completed":
                job_stats[job_name]["success"] += 1
            else:
                job_stats[job_name]["failed"] += 1
                
            # Time stats
            time_stats[hour]["total"] += 1
            if status == "completed":
                time_stats[hour]["success"] += 1
            else:
                time_stats[hour]["failed"] += 1
                
            # Day stats
            day_stats[day]["total"] += 1
            if status == "completed":
                day_stats[day]["success"] += 1
            else:
                day_stats[day]["failed"] += 1
                
        # Calculate success rates
        for job_id, stats in job_stats.items():
            if stats["total"] > 0:
                rate = stats["success"] / stats["total"]
                self.data["job_performance"][job_id] = {
                    "rate": rate,
                    "total": stats["total"]
                }
                
        for hour, stats in time_stats.items():
            if stats["total"] > 0:
                rate = stats["success"] / stats["total"]
                self.data["time_performance"][str(hour)] = {
                    "rate": rate,
                    "total": stats["total"]
                }
                
        for day, stats in day_stats.items():
            if stats["total"] > 0:
                rate = stats["success"] / stats["total"]
                self.data["day_performance"][str(day)] = {
                    "rate": rate,
                    "total": stats["total"]
                }
                
        self.data["last_analysis"] = datetime.now().isoformat()
        self.save_analysis()
        
        return {
            "jobs": job_stats,
            "hours": time_stats,
            "days": day_stats
        }
        
    def get_optimal_schedule(self):
        """Suggest optimal times based on learning"""
        best_hour = None
        best_rate = 0
        
        for hour, data in self.data["time_performance"].items():
            if data["total"] >= 5 and data["rate"] > best_rate:
                best_rate = data["rate"]
                best_hour = hour
                
        return best_hour, best_rate
        
    def get_failing_jobs(self):
        """Get jobs that are failing often"""
        failing = []
        for job_id, data in self.data["job_performance"].items():
            if data["rate"] < 0.7 and data["total"] >= 3:
                failing.append({
                    "job": job_id,
                    "rate": data["rate"],
                    "total": data["total"]
                })
        return failing

if __name__ == "__main__":
    analyzer = CronAnalyzer()
    results = analyzer.analyze_cron_jobs()
    
    print("📊 Cron Performance Analysis")
    print("=" * 40)
    
    if results:
        # Show best times
        best_hour, best_rate = analyzer.get_optimal_schedule()
        if best_hour:
            print(f"🕐 Best hour: {best_hour}:00 ({int(best_rate*100)}% success)")
            
        # Show failing jobs
        failing = analyzer.get_failing_jobs()
        if failing:
            print("\n⚠️ Jobs needing attention:")
            for job in failing:
                print(f"  - {job['job']}: {int(job['rate']*100)}% success ({job['total']} runs)")
        else:
            print("\n✅ All jobs performing well!")
    else:
        print("No data available yet")
        
    print(f"\nLast analysis: {analyzer.data.get('last_analysis', 'Never')}")
