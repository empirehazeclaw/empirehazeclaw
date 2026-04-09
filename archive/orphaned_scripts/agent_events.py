#!/usr/bin/env python3
"""
Real-time Agent Events - Simple SSE
"""

import json
from flask import Flask, Response
import redis

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

CHANNEL = "agent:events"

@app.route('/events')
def events():
    def generate():
        pubsub = r.pubsub()
        pubsub.subscribe(CHANNEL)
        for msg in pubsub.listen():
            if msg['type'] == 'message':
                yield f"data: {msg['data']}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/emit/<agent>/<event_type>')
def emit(agent, event_type):
    data = {"agent": agent, "type": event_type, "time": json.dumps(__import__('datetime').datetime.now())}
    r.publish(CHANNEL, json.dumps(data))
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(port=8893)
