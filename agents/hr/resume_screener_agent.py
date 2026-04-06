#!/usr/bin/env python3
"""
Resume Screener Agent
Screens resumes against job requirements and ranks candidates.
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/hr")
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "resume_screener.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

RESUME_FILE = DATA_DIR / "resumes.json"
JOB_FILE = DATA_DIR / "jobs.json"
RESULTS_FILE = DATA_DIR / "screening_results.json"


def load_json(path: Path, default: Any = None) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text())
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading {path}: {e}")
    return default if default is not None else {}


def save_json(path: Path, data: Any) -> bool:
    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        return True
    except IOError as e:
        logger.error(f"Error saving {path}: {e}")
        return False


def extract_skills(text: str) -> list[str]:
    """Extract skills from text, case-insensitive."""
    text_lower = text.lower()
    common_skills = [
        "python", "java", "javascript", "typescript", "go", "rust", "c++", "c#",
        "react", "angular", "vue", "node.js", "nodejs", "django", "flask", "fastapi",
        "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
        "git", "ci/cd", "jenkins", "github actions",
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "agile", "scrum", "kanban", "jira",
        "html", "css", "sass", "webpack",
        "api", "rest", "graphql", "grpc",
        "linux", "bash", "shell",
        "project management", "team lead", "communication"
    ]
    found = []
    for skill in common_skills:
        if skill.lower() in text_lower:
            found.append(skill.lower())
    return list(set(found))


def score_resume(resume: dict, job: dict) -> dict:
    """Score a resume against job requirements."""
    resume_text = json.dumps(resume).lower()
    job_text = json.dumps(job).lower()
    
    # Required skills scoring
    required_skills = [s.lower() for s in job.get("required_skills", [])]
    optional_skills = [s.lower() for s in job.get("optional_skills", [])]
    
    found_required = sum(1 for s in required_skills if s in resume_text)
    found_optional = sum(1 for s in optional_skills if s in resume_text)
    
    required_score = (found_required / max(len(required_skills), 1)) * 100
    optional_score = (found_optional / max(len(optional_skills), 1)) * 50
    
    # Experience scoring
    years_exp = resume.get("years_experience", 0)
    min_exp = job.get("min_experience_years", 0)
    exp_score = min(100, (years_exp / max(min_exp, 1)) * 100) if years_exp >= min_exp else 0
    
    # Education scoring
    edu_match = 0
    resume_edu = resume.get("education", "").lower()
    for edu in job.get("education_levels", []):
        if edu.lower() in resume_edu:
            edu_match = {"high_school": 50, "bachelor": 75, "master": 90, "phd": 100}.get(edu.lower(), 60)
            break
    
    # Total weighted score
    total_score = (
        required_score * 0.40 +
        optional_score * 0.15 +
        exp_score * 0.25 +
        edu_match * 0.20
    )
    
    return {
        "candidate_id": resume.get("id", "unknown"),
        "candidate_name": resume.get("name", "Unknown"),
        "total_score": round(total_score, 1),
        "breakdown": {
            "required_skills": f"{found_required}/{len(required_skills)}",
            "optional_skills": f"{found_optional}/{len(optional_skills)}",
            "experience_years": years_exp,
            "education_match": edu_match
        },
        "matched_skills": [s for s in required_skills + optional_skills if s in resume_text],
        "status": "reviewed"
    }


def screen_resumes(job_id: str) -> list[dict]:
    """Screen all resumes for a specific job."""
    jobs = load_json(JOB_FILE, {"jobs": []})["jobs"]
    job = next((j for j in jobs if j.get("id") == job_id), None)
    if not job:
        logger.error(f"Job not found: {job_id}")
        return []
    
    resumes = load_json(RESUME_FILE, {"resumes": []})["resumes"]
    if not resumes:
        logger.warning("No resumes found in database")
        return []
    
    logger.info(f"Screening {len(resumes)} resumes for job: {job.get('title', job_id)}")
    
    results = []
    for resume in resumes:
        score = score_resume(resume, job)
        score["job_id"] = job_id
        score["screened_at"] = datetime.utcnow().isoformat()
        results.append(score)
    
    # Sort by score descending
    results.sort(key=lambda x: x["total_score"], reverse=True)
    
    # Assign rank
    for i, r in enumerate(results):
        r["rank"] = i + 1
    
    return results


def list_resumes() -> list[dict]:
    """List all resumes in the database."""
    data = load_json(RESUME_FILE, {"resumes": []})
    return data.get("resumes", [])


def add_resume(resume_data: dict) -> bool:
    """Add a new resume to the database."""
    resumes = load_json(RESUME_FILE, {"resumes": []})
    resume_id = resume_data.get("id", f"resume_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
    resume_data["id"] = resume_id
    resume_data["added_at"] = datetime.utcnow().isoformat()
    resume_data["skills"] = extract_skills(json.dumps(resume_data))
    resumes["resumes"].append(resume_data)
    return save_json(RESUME_FILE, resumes)


def add_job(job_data: dict) -> bool:
    """Add a new job to the database."""
    jobs = load_json(JOB_FILE, {"jobs": []})
    job_id = job_data.get("id", f"job_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
    job_data["id"] = job_id
    job_data["created_at"] = datetime.utcnow().isoformat()
    jobs["jobs"].append(job_data)
    return save_json(JOB_FILE, jobs)


def get_results(job_id: str = None) -> list[dict]:
    """Get screening results."""
    results = load_json(RESULTS_FILE, {"results": []})
    data = results.get("results", [])
    if job_id:
        data = [r for r in data if r.get("job_id") == job_id]
    return data


def save_results(results: list[dict]) -> bool:
    """Save screening results."""
    data = load_json(RESULTS_FILE, {"results": []})
    data["results"].extend(results)
    return save_json(RESULTS_FILE, data)


def cmd_screen(args):
    """Screen resumes for a job."""
    if not args.job_id:
        print("Error: --job-id is required for screening")
        sys.exit(1)
    
    results = screen_resumes(args.job_id)
    if results:
        save_results(results)
        print(f"\n{'='*60}")
        print(f"SCREENING RESULTS FOR JOB: {args.job_id}")
        print(f"{'='*60}\n")
        for r in results:
            status_icon = "✅" if r["total_score"] >= 70 else "⚠️" if r["total_score"] >= 50 else "❌"
            print(f"{status_icon} #{r['rank']} {r['candidate_name']} - Score: {r['total_score']}%")
            print(f"   Skills: {', '.join(r['matched_skills'][:5]) or 'None matched'}")
            print(f"   Breakdown: {r['breakdown']}")
            print()
    else:
        print(f"No results for job: {args.job_id}")
        print("Add jobs and resumes first using --add-job and --add-resume")


def cmd_list_resumes(args):
    """List all resumes."""
    resumes = list_resumes()
    if not resumes:
        print("No resumes in database. Add resumes with --add-resume")
        return
    print(f"\n{'='*60}")
    print(f"RESUMES IN DATABASE: {len(resumes)}")
    print(f"{'='*60}\n")
    for r in resumes:
        print(f"📄 {r.get('name', 'Unknown')} (ID: {r.get('id')})")
        print(f"   Experience: {r.get('years_experience', 0)} years")
        print(f"   Skills: {', '.join(r.get('skills', [])[:8])}")
        print(f"   Education: {r.get('education', 'Not specified')}")
        print()


def cmd_list_jobs(args):
    """List all jobs."""
    jobs = load_json(JOB_FILE, {"jobs": []}).get("jobs", [])
    if not jobs:
        print("No jobs in database. Add jobs with --add-job")
        return
    print(f"\n{'='*60}")
    print(f"JOBS IN DATABASE: {len(jobs)}")
    print(f"{'='*60}\n")
    for j in jobs:
        print(f"💼 {j.get('title', 'Unknown')} (ID: {j.get('id')})")
        print(f"   Department: {j.get('department', 'N/A')}")
        print(f"   Required Skills: {', '.join(j.get('required_skills', [])[:5])}")
        print()


def cmd_add_resume(args):
    """Add a resume interactively."""
    print("\n--- Add New Resume ---")
    resume = {}
    resume["name"] = input("Candidate Name: ").strip()
    if not resume["name"]:
        print("Name is required")
        return
    
    try:
        resume["years_experience"] = int(input("Years of Experience: ").strip() or "0")
    except ValueError:
        resume["years_experience"] = 0
    
    resume["education"] = input("Education (e.g., Bachelor in Computer Science): ").strip()
    resume["skills"] = input("Skills (comma-separated): ").strip().split(",")
    resume["skills"] = [s.strip() for s in resume["skills"] if s.strip()]
    
    resume["email"] = input("Email: ").strip()
    resume["phone"] = input("Phone: ").strip()
    resume["current_title"] = input("Current Title: ").strip()
    resume["summary"] = input("Summary/Notes: ").strip()
    
    if add_resume(resume):
        print(f"✅ Resume added successfully!")
    else:
        print("❌ Failed to save resume")


def cmd_add_job(args):
    """Add a job interactively."""
    print("\n--- Add New Job ---")
    job = {}
    job["title"] = input("Job Title: ").strip()
    if not job["title"]:
        print("Title is required")
        return
    
    job["department"] = input("Department: ").strip()
    
    required = input("Required Skills (comma-separated): ").strip()
    job["required_skills"] = [s.strip() for s in required.split(",") if s.strip()]
    
    optional = input("Optional Skills (comma-separated): ").strip()
    job["optional_skills"] = [s.strip() for s in optional.split(",") if s.strip()]
    
    try:
        job["min_experience_years"] = int(input("Min Experience Years: ").strip() or "0")
    except ValueError:
        job["min_experience_years"] = 0
    
    edu_levels = input("Education Levels (comma-separated: high_school, bachelor, master, phd): ").strip()
    job["education_levels"] = [e.strip() for e in edu_levels.split(",") if e.strip()]
    
    if add_job(job):
        print(f"✅ Job added successfully!")
    else:
        print("❌ Failed to save job")


def cmd_export(args):
    """Export screening results to JSON."""
    results = get_results(args.job_id)
    if not results:
        print("No results to export")
        return
    
    output_path = Path(args.output) if args.output else DATA_DIR / f"export_{datetime.utcnow().strftime('%Y%m%d')}.json"
    save_json(output_path, {"results": results, "exported_at": datetime.utcnow().isoformat()})
    print(f"✅ Exported {len(results)} results to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Resume Screener Agent - Screen resumes against job requirements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list-resumes
  %(prog)s --list-jobs
  %(prog)s --add-resume
  %(prog)s --add-job
  %(prog)s --screen --job-id job_001
  %(prog)s --screen --job-id job_001 --export results.json
        """
    )
    
    parser.add_argument("--screen", action="store_true", help="Screen resumes for a job")
    parser.add_argument("--job-id", type=str, help="Job ID to screen against")
    parser.add_argument("--list-resumes", action="store_true", help="List all resumes")
    parser.add_argument("--list-jobs", action="store_true", help="List all jobs")
    parser.add_argument("--add-resume", action="store_true", help="Add a new resume")
    parser.add_argument("--add-job", action="store_true", help="Add a new job posting")
    parser.add_argument("--export", type=str, metavar="FILE", help="Export results to JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.screen:
        cmd_screen(args)
    elif args.list_resumes:
        cmd_list_resumes(args)
    elif args.list_jobs:
        cmd_list_jobs(args)
    elif args.add_resume:
        cmd_add_resume(args)
    elif args.add_job:
        cmd_add_job(args)
    elif args.export:
        cmd_export(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
