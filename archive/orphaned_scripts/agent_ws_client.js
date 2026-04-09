#!/usr/bin/env node

/**
 * 🤖 Agent WebSocket Client
 * ========================
 * Connect any OpenClaw agent to the WebSocket Gateway
 */

const WebSocket = require('ws');

class AgentWSClient {
  constructor(agentId, capabilities = []) {
    this.agentId = agentId;
    this.capabilities = capabilities;
    this.ws = null;
    this.pendingRequests = new Map();
    this.messageHandler = null;
  }
  
  connect(wsUrl = 'ws://localhost:18790') {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.on('open', () => {
        console.log(`✅ Connected as ${this.agentId}`);
        
        // Register
        this.send({
          type: 'register',
          agentId: this.agentId,
          name: this.agentId,
          capabilities: this.capabilities
        });
        
        resolve();
      });
      
      this.ws.on('message', (data) => {
        try {
          const msg = JSON.parse(data);
          this.handleMessage(msg);
        } catch (e) {
          console.error('❌ Parse error:', e.message);
        }
      });
      
      this.ws.on('close', () => {
        console.log('📴 Disconnected');
        this.reconnect();
      });
      
      this.ws.on('error', (e) => {
        console.error('❌ Error:', e.message);
        reject(e);
      });
    });
  }
  
  send(obj) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(obj));
    }
  }
  
  handleMessage(msg) {
    console.log(`📨 ${msg.type}:`, msg);
    
    switch (msg.type) {
      case 'message':
        if (this.messageHandler) {
          this.messageHandler(msg);
        }
        break;
        
      case 'request':
        // Handle request - respond with response type
        this.handleRequest(msg);
        break;
        
      case 'response':
        const pending = this.pendingRequests.get(msg.requestId);
        if (pending) {
          pending.resolve(msg.data || msg.error);
          this.pendingRequests.delete(msg.requestId);
        }
        break;
        
      case 'broadcast':
        if (this.messageHandler) {
          this.messageHandler(msg);
        }
        break;
        
      case 'pong':
        // Heartbeat response
        break;
    }
  }
  
  handleRequest(msg) {
    // Default: acknowledge receipt
    // Override in subclass for custom handling
    this.send({
      type: 'response',
      requestId: msg.requestId,
      data: { received: true, action: msg.action }
    });
  }
  
  sendTo(targetAgentId, content, priority = 'normal') {
    this.send({
      type: 'send_to',
      target: targetAgentId,
      content,
      priority
    });
  }
  
  broadcast(content) {
    this.send({
      type: 'broadcast',
      content
    });
  }
  
  async request(targetAgentId, action, data = {}) {
    const requestId = `req_${Date.now()}`;
    
    return new Promise((resolve, reject) => {
      this.pendingRequests.set(requestId, { resolve, reject });
      
      this.send({
        type: 'request',
        requestId,
        target: targetAgentId,
        action,
        data
      });
      
      // Timeout after 30s
      setTimeout(() => {
        if (this.pendingRequests.has(requestId)) {
          this.pendingRequests.delete(requestId);
          reject(new Error('Request timeout'));
        }
      }, 30000);
    });
  }
  
  reconnect() {
    console.log('🔄 Reconnecting in 5s...');
    setTimeout(() => {
      this.connect().catch(console.error);
    }, 5000);
  }
  
  onMessage(handler) {
    this.messageHandler = handler;
  }
}

// CLI usage
if (require.main === module) {
  const agentId = process.argv[2] || 'test-agent';
  const capabilities = process.argv[3] ? process.argv[3].split(',') : [];
  
  const client = new AgentWSClient(agentId, capabilities);
  
  client.connect().then(() => {
    console.log(`🤖 Agent ${agentId} ready!`);
    
    // Test broadcast after 2s
    setTimeout(() => {
      client.broadcast(`Hello from ${agentId}!`);
    }, 2000);
    
    // Keep alive
    setInterval(() => {
      client.send({ type: 'ping' });
    }, 25000);
  }).catch(console.error);
}

module.exports = { AgentWSClient };
