#!/usr/bin/env python3
"""
Unified API Gateway for EmpireHazeClaw Services
Single entry point for all microservices
"""
from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

# Service endpoints
SERVICES = {
    'chatbot': 'http://localhost:8896',
    'leadgen': 'http://localhost:8895', 
    'trading': 'http://localhost:8001',
    'discord': 'http://localhost:8892',
    'seo': 'http://localhost:8898'
}

@app.route('/')
def index():
    return jsonify({
        'service': 'EmpireHazeClaw API Gateway',
        'version': '1.0',
        'status': 'operational',
        'services': list(SERVICES.keys())
    })

@app.route('/health')
def health():
    available = []
    for name, url in SERVICES.items():
        try:
            r = requests.get(f'{url}/health', timeout=1)
            if r.status_code == 200:
                available.append(name)
        except:
            pass
    return jsonify({'status': 'healthy', 'services': available})

@app.route('/api/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(service, path):
    if service not in SERVICES:
        return jsonify({'error': f'Unknown service: {service}'}), 404
    
    url = f"{SERVICES[service]}/{path}"
    try:
        if request.method == 'GET':
            resp = requests.get(url, params=request.args, headers=request.headers)
        elif request.method == 'POST':
            resp = requests.post(url, json=request.json, headers=request.headers)
        elif request.method == 'PUT':
            resp = requests.put(url, json=request.json, headers=request.headers)
        elif request.method == 'DELETE':
            resp = requests.delete(url, headers=request.headers)
        
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 502

@app.route('/services')
def list_services():
    return jsonify(SERVICES)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8891, debug=False)
