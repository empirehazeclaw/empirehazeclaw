#!/usr/bin/env python3
"""
Cron Cleanup Script
Cleans up old cron failure records and analyzes job performance
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta

CRON_DB_PATH = "/home/clawbot/.openclaw/cron-automation/cron.db"

def get_connection():
    """Get database connection"""
    return sqlite3.connect(CRON_DB_PATH)

def analyze_failures():
    """Analyze cron failures"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all failures
    cursor.execute("SELECT * FROM cron_failures ORDER BY failed_at DESC")
    failures = cursor.fetchall()
    
    print(f"\n📊 Total failures recorded: {len(failures)}")
    
    if failures:
        # Group by job name
        failure_counts = {}
        for f in failures:
            job_name = f[1]
            failure_counts[job_name] = failure_counts.get(job_name, 0) + 1
        
        print("\n⚠️ Failures by job:")
        for job, count in sorted(failure_counts.items(), key=lambda x: -x[1]):
            print(f"  - {job}: {count} failures")
    
    conn.close()
    return failures

def analyze_runs():
    """Analyze cron job runs"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get recent runs
    cursor.execute("""
        SELECT job_name, status, COUNT(*) as count, 
               AVG(duration_ms) as avg_duration
        FROM cron_runs 
        WHERE start_time > datetime('now', '-7 days')
        GROUP BY job_name, status
        ORDER BY count DESC
    """)
    runs = cursor.fetchall()
    
    print(f"\n📈 Cron runs (last 7 days):")
    
    if runs:
        for job_name, status, count, avg_duration in runs:
            status_icon = "✅" if status == "success" else "❌"
            print(f"  {status_icon} {job_name}: {count} runs, avg {avg_duration:.0f}ms")
    else:
        print("  No runs recorded")
    
    conn.close()

def cleanup_old_records(days=30):
    """Clean up old failure records"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cutoff = datetime.now() - timedelta(days=days)
    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")
    
    # Delete old failures
    cursor.execute("DELETE FROM cron_failures WHERE failed_at < ?", (cutoff_str,))
    deleted_failures = cursor.rowcount
    
    # Delete old runs
    cursor.execute("DELETE FROM cron_runs WHERE start_time < ?", (cutoff_str,))
    deleted_runs = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"\n🧹 Cleanup complete:")
    print(f"  - Deleted {deleted_failures} old failure records")
    print(f"  - Deleted {deleted_runs} old run records")

def main():
    """Main entry point"""
    print("=" * 50)
    print("🧹 Cron Cleanup Tool")
    print("=" * 50)
    
    if not os.path.exists(CRON_DB_PATH):
        print("❌ Cron database not found")
        return
    
    # Analyze
    analyze_failures()
    analyze_runs()
    
    # Cleanup old records (older than 30 days)
    print("\n" + "-" * 50)
    cleanup_old_records(days=30)
    
    print("\n✅ Cron cleanup complete")

if __name__ == "__main__":
    main()
