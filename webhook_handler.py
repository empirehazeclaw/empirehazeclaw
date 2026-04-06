#!/usr/bin/env python3
"""
🌐 WEBHOOK HANDLER
=================
Receives tasks from external sources and adds to queue
"""

from flask import Flask, request, jsonify
import json
import subprocess

app = Flask(__name__)

@app.route("/webhook/task", methods=["POST"])
def receive_task():
    """Receive task from webhook"""
    data = request.json
    
    task = data.get("task", "")
    agent = data.get("agent", None)
    priority = data.get("priority", "normal")
    
    if not task:
        return jsonify({"error": "No task provided"}), 400
    
    # Add to task queue
    result = subprocess.run(
        ["python3", "scripts/task_scheduler.py", "add", task] + 
        (["--agent", agent] if agent else []),
        capture_output=True,
        text=True
    )
    
    return jsonify({
        "status": "queued",
        "task": task,
        "agent": agent
    })

@app.route("/webhook/trigger", methods=["POST"])
def trigger_workflow():
    """Trigger predefined workflow"""
    workflow = request.json.get("workflow")
    
    workflows = {
        "morning": [
            {"task": "Research latest AI trends", "agent": "research"},
            {"task": "Post to Twitter", "agent": "growth"},
            {"task": "Send outreach emails", "agent": "revenue"}
        ],
        "content": [
            {"task": "Write blog post", "agent": "content"}
        ]
    }
    
    if workflow not in workflows:
        return jsonify({"error": "Unknown workflow"}), 400
    
    for item in workflows[workflow]:
        subprocess.run(
            ["python3", "scripts/task_scheduler.py", "add", item["task"], "--agent", item["agent"]],
            capture_output=True
        )
    
    return jsonify({"status": "queued", "workflow": workflow, "tasks": len(workflows[workflow])})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
