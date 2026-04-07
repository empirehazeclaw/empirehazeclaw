#!/usr/bin/env node

/**
 * 🔌 WebSocket Agent Gateway
 * ==========================
 * Echtzeit-Agent-zu-Agent Kommunikation via WebSocket
 * 
 * Features:
 * - Bidirectional messaging
 * - Real-time events
 * - Agent presence/online status
 * - Message queuing
 */

const WebSocket = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 18790;
const AGENTS_FILE = '/home/clawbot/.openclaw/workspace/config/registered_agents.json';

// WebSocket clients (agents)
const agents = new Map();
const messageQueue = new Map();

// HTTP Server for status
const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', agents: agents.size }));
  } else if (req.url === '/agents') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      connected: Array.from(agents.keys()),
      queue: messageQueue.size
    }));
  } else {
    res.writeHead(404);
    res.end();
  }
});

// WebSocket Server
const wss = new WebSocket.Server({ server });

console.log(`🔌 Starting WebSocket Agent Gateway on port ${PORT}...`);

wss.on('connection', (ws, req) => {
  const agentId = `agent_${Date.now()}`;
  console.log(`📡 New connection: ${agentId}`);
  
  // Register agent
  agents.set(agentId, {
    ws,
    id: agentId,
    connectedAt: new Date().toISOString(),
    lastActivity: Date.now()
  });
  
  // Send welcome
  ws.send(JSON.stringify({
    type: 'welcome',
    agentId,
    message: 'Connected to Agent WebSocket Gateway'
  }));
  
  // Handle messages
  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data);
      handleMessage(agentId, msg);
      
      // Update last activity
      const agent = agents.get(agentId);
      if (agent) agent.lastActivity = Date.now();
    } catch (e) {
      console.error(`❌ Invalid message from ${agentId}:`, e.message);
    }
  });
  
  // Handle disconnect
  ws.on('close', () => {
    console.log(`📴 Disconnected: ${agentId}`);
    agents.delete(agentId);
    
    // Notify others
    broadcast({
      type: 'agent_offline',
      agentId
    }, agentId);
  });
  
  // Notify others of new agent
  broadcast({
    type: 'agent_online',
    agentId,
    agents: Array.from(agents.keys())
  }, agentId);
});

function handleMessage(senderId, msg) {
  console.log(`📨 Message from ${senderId}:`, msg.type);
  
  switch (msg.type) {
    case 'register':
      // Agent registers with name
      const agent = agents.get(senderId);
      if (agent) {
        agent.id = msg.agentId || senderId;
        agent.name = msg.name;
        agent.capabilities = msg.capabilities || [];
        
        // Load full registry
        try {
          const registry = JSON.parse(fs.readFileSync(AGENTS_FILE, 'utf8'));
          const existing = registry.agents.find(a => a.name === agent.id);
          if (existing) {
            Object.assign(agent, existing);
          }
        } catch (e) {}
        
        console.log(`✅ Agent registered: ${agent.id}`);
      }
      break;
    
    case 'send_to':
      // Direct message to another agent
      sendToAgent(msg.target, {
        type: 'message',
        from: senderId,
        fromName: agents.get(senderId)?.name,
        content: msg.content,
        priority: msg.priority || 'normal'
      });
      break;
    
    case 'broadcast':
      // Broadcast to all
      broadcast({
        type: 'broadcast',
        from: senderId,
        fromName: agents.get(senderId)?.name,
        content: msg.content
      }, senderId);
      break;
    
    case 'request':
      // Request-response pattern
      handleRequest(senderId, msg);
      break;
    
    case 'response':
      // Response to a request
      completeRequest(senderId, msg);
      break;
    
    case 'ping':
      ws = agents.get(senderId)?.ws;
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'pong', timestamp: Date.now() }));
      }
      break;
      
    default:
      console.log(`⚠️ Unknown message type: ${msg.type}`);
  }
}

function sendToAgent(targetId, message) {
  const agent = agents.get(targetId);
  
  if (agent && agent.ws.readyState === WebSocket.OPEN) {
    agent.ws.send(JSON.stringify(message));
    console.log(`📤 Sent to ${targetId}`);
    return true;
  } else {
    // Queue message for later
    if (!messageQueue.has(targetId)) {
      messageQueue.set(targetId, []);
    }
    messageQueue.get(targetId).push(message);
    console.log(`📬 Queued message for ${targetId} (offline)`);
    return false;
  }
}

function broadcast(message, excludeId = null) {
  let sent = 0;
  agents.forEach((agent, id) => {
    if (id !== excludeId && agent.ws.readyState === WebSocket.OPEN) {
      agent.ws.send(JSON.stringify(message));
      sent++;
    }
  });
  console.log(`📣 Broadcast to ${sent} agents`);
}

const pendingRequests = new Map();

function handleRequest(requesterId, msg) {
  const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  pendingRequests.set(requestId, {
    requesterId,
    request: msg,
    createdAt: Date.now()
  });
  
  // Forward to target
  const sent = sendToAgent(msg.target, {
    type: 'request',
    requestId,
    from: requesterId,
    fromName: agents.get(requesterId)?.name,
    action: msg.action,
    data: msg.data
  });
  
  // Timeout after 30 seconds
  setTimeout(() => {
    if (pendingRequests.has(requestId)) {
      sendToAgent(requesterId, {
        type: 'response',
        requestId,
        error: 'Timeout'
      });
      pendingRequests.delete(requestId);
    }
  }, 30000);
}

function completeRequest(requesterId, msg) {
  const pending = pendingRequests.get(msg.requestId);
  if (pending) {
    sendToAgent(pending.requesterId, {
      type: 'response',
      requestId: msg.requestId,
      data: msg.data,
      error: msg.error
    });
    pendingRequests.delete(msg.requestId);
  }
}

// Send queued messages when agent reconnects
function checkQueuedMessages(agentId) {
  if (messageQueue.has(agentId)) {
    const queue = messageQueue.get(agentId);
    const agent = agents.get(agentId);
    
    if (agent && agent.ws.readyState === WebSocket.OPEN) {
      queue.forEach(msg => {
        agent.ws.send(JSON.stringify(msg));
      });
      queue.length = 0;
      console.log(`📬 Sent ${queue.length} queued messages to ${agentId}`);
    }
  }
}

// Health check - remove stale connections
setInterval(() => {
  const now = Date.now();
  agents.forEach((agent, id) => {
    if (now - agent.lastActivity > 60000) {
      // Ping to check
      if (agent.ws.readyState === WebSocket.OPEN) {
        agent.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }
  });
  
  // Check queued messages
  agents.forEach((agent, id) => {
    checkQueuedMessages(id);
  });
}, 30000);

// Start server
server.listen(PORT, () => {
  console.log(`✅ WebSocket Gateway running on ws://localhost:${PORT}`);
  console.log(`   HTTP Status: http://localhost:${PORT}/health`);
});
