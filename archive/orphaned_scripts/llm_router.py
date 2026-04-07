#!/usr/bin/env python3
"""
🎯 LLM Router v5.0
Smart Caching + Load Balancing + Automatic Fallback
"""

import os, json, time, argparse, hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import *
from dataclasses import dataclass, field
from collections import defaultdict
import threading

@dataclass(eq=False)
class Model:
    name: str
    provider: str
    api_key_env: str
    model_string: str
    context_window: int
    is_free: bool
    is_fast: bool
    speed_score: int
    quality_score: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    strengths: List[str] = field(default_factory=list)
    best_for: List[str] = field(default_factory=list)
    supports_vision: bool = False
    supports_function_calling: bool = False

# MODEL REGISTRY
MODEL_REGISTRY = [
    Model("Gemini 2.5 Flash","Google","GEMINI_API_KEY","gemini-2.5-flash",1000000,True,True,9,8,0,0,["fast","multimodal"],["reasoning","coding"],True,True),
    Model("Gemini 2.5 Pro","Google","GEMINI_API_KEY","gemini-2.5-pro",2000000,True,False,7,9,0,0,["large context","reasoning"],["analysis"],True,True),
    Model("DeepSeek R1","HuggingFace","HUGGINGFACE_API_KEY","deepseek-ai/DeepSeek-R1",64000,True,False,6,10,0,0,["reasoning"],["problem solving"],False,True),
    Model("DeepSeek R1 Distill","OpenRouter","OPENROUTER_API_KEY","deepseek/deepseek-r1-distill-qwen-32b",32000,True,True,8,9,0,0,["fast reasoning"],["coding"],False,True),
    Model("Claude 3.5 Sonnet","Anthropic","ANTHROPIC_API_KEY","claude-sonnet-4-20250514",200000,False,False,7,10,0.003,0.015,["reasoning"],["coding","analysis"],True,True),
    Model("GPT-4o","OpenAI","OPENAI_API_KEY","gpt-4o",128000,False,False,7,10,0.005,0.015,["excellent"],["coding","reasoning"],True,True),
]

# FALLBACK CHAINS
FALLBACK_CHAINS = {
    "speed": ["Gemini 2.5 Flash","Gemini 2.5 Pro"],
    "quality": ["Gemini 2.5 Pro","Gemini 2.5 Flash","Claude 3.5 Sonnet","GPT-4o"],
    "cost": ["Gemini 2.5 Flash","Gemini 2.5 Pro"],
    "balanced": ["Gemini 2.5 Flash","Gemini 2.5 Pro"],
}


# ═══════════════════════════════════════════════════════════════
# 🧠 SEMANTIC CACHE
# ═══════════════════════════════════════════════════════════════
class SemanticCache:
    """
    Hash-based cache with TTL and similarity matching.
    """
    def __init__(self, db_path: str = None, ttl_seconds: int = 3600):
        self.db_path = Path(db_path or "/home/clawbot/.openclaw/workspace/data/llm_cache.json")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_seconds
        self.cache = self._load()
        self.hits = 0
        self.misses = 0
        self.lock = threading.Lock()
    
    def _load(self) -> dict:
        if self.db_path.exists():
            return json.loads(self.db_path.read_text())
        return {"entries": {}, "stats": {"hits": 0, "misses": 0}}
    
    def _save(self):
        self.db_path.write_text(json.dumps(self.cache, indent=2))
    
    def _hash(self, text: str) -> str:
        """Simple hash for cache key."""
        return hashlib.sha256(text.lower().strip()[:500].encode()).hexdigest()[:16]
    
    def get(self, prompt: str) -> Optional[str]:
        """Get cached response if exists and not expired."""
        key = self._hash(prompt)
        
        with self.lock:
            if key in self.cache["entries"]:
                entry = self.cache["entries"][key]
                age = time.time() - entry["timestamp"]
                
                if age < self.ttl:
                    self.hits += 1
                    self.cache["stats"]["hits"] += 1
                    self._save()
                    return entry["response"]
                else:
                    del self.cache["entries"][key]
            
            self.misses += 1
            self.cache["stats"]["misses"] += 1
            self._save()
            return None
    
    def set(self, prompt: str, response: str):
        """Cache a response."""
        key = self._hash(prompt)
        
        with self.lock:
            self.cache["entries"][key] = {
                "prompt": prompt[:100],
                "response": response,
                "timestamp": time.time()
            }
            self._save()
    
    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / max(total, 1) * 100,
            "entries": len(self.cache["entries"]),
            "saved_cost": self.hits * 0.001  # rough estimate
        }


# ═══════════════════════════════════════════════════════════════
# 🔀 LOAD BALANCER
# ═══════════════════════════════════════════════════════════════
class LoadBalancer:
    """
    Routes requests across multiple models using different strategies.
    """
    def __init__(self):
        self.model_usage = defaultdict(int)  # Track usage per model
        self.model_latency = defaultdict(list)  # Track latency per model
        self.lock = threading.Lock()
    
    def select(self, available_models: List[Model], strategy: str = "round_robin") -> Model:
        """
        Select model based on strategy.
        Strategies: round_robin, least_used, fastest_avg, weighted
        """
        if not available_models:
            raise ValueError("No models available")
        
        with self.lock:
            if strategy == "round_robin":
                # Simple round-robin
                for m in available_models:
                    self.model_usage[m.name] += 1
                    return m
            
            elif strategy == "least_used":
                # Pick model with lowest usage
                usage = {m.name: self.model_usage.get(m.name, 0) for m in available_models}
                selected = min(usage, key=usage.get)
                self.model_usage[selected] += 1
                return next(m for m in available_models if m.name == selected)
            
            elif strategy == "fastest_avg":
                # Pick model with best average latency
                latencies = {}
                for m in available_models:
                    if self.model_latency[m.name]:
                        latencies[m.name] = sum(self.model_latency[m.name]) / len(self.model_latency[m.name])
                    else:
                        latencies[m.name] = 1000  # Default high
                
                fastest = min(latencies, key=latencies.get)
                self.model_usage[fastest] += 1
                return next(m for m in available_models if m.name == fastest)
            
            elif strategy == "weighted":
                # Weight by speed score
                total_weight = sum(m.speed_score for m in available_models)
                import random
                r = random.uniform(0, total_weight)
                cumulative = 0
                for m in available_models:
                    cumulative += m.speed_score
                    if r <= cumulative:
                        self.model_usage[m.name] += 1
                        return m
                return available_models[0]
            
            else:
                return available_models[0]
    
    def record_latency(self, model_name: str, latency_ms: int):
        """Record latency for a model."""
        with self.lock:
            self.model_latency[model_name].append(latency_ms)
            # Keep last 10 latencies
            if len(self.model_latency[model_name]) > 10:
                self.model_latency[model_name] = self.model_latency[model_name][-10:]
    
    def stats(self) -> dict:
        with self.lock:
            return {
                "usage": dict(self.model_usage),
                "avg_latency": {
                    m: sum(lats)/len(lats) if lats else 0 
                    for m, lats in self.model_latency.items()
                }
            }


# ═══════════════════════════════════════════════════════════════
# 📊 USAGE TRACKER
# ═══════════════════════════════════════════════════════════════
class UsageTracker:
    def __init__(self):
        self.db = Path("/home/clawbot/.openclaw/workspace/data/llm_usage.json")
        self.db.parent.mkdir(parents=True, exist_ok=True)
        self.data = {"requests": [], "daily_costs": {}, "model_stats": {}}
        if self.db.exists():
            self.data = json.loads(self.db.read_text())
    
    def save(self):
        self.db.write_text(json.dumps(self.data, indent=2))
    
    def record(self, model, provider, success, latency, cost, error=None):
        today = datetime.now().date().isoformat()
        self.data.setdefault("daily_costs", {}).setdefault(today, 0)
        self.data["daily_costs"][today] += cost
        stats = self.data.setdefault("model_stats", {}).setdefault(model, {"requests": 0, "success": 0, "errors": 0})
        stats["requests"] += 1
        if success: stats["success"] += 1
        else: stats["errors"] += 1
        self.data["requests"].append({"timestamp": datetime.now().isoformat(), "model": model, "provider": provider, "success": success, "latency": latency, "cost": cost, "error": error})
        cutoff = (datetime.now() - timedelta(30)).date().isoformat()
        self.data["daily_costs"] = {k:v for k,v in self.data["daily_costs"].items() if k >= cutoff}
        self.data["requests"] = [r for r in self.data["requests"] if r["timestamp"] >= cutoff]
        self.save()
    
    def stats(self):
        recent = [r for r in self.data["requests"] if r["timestamp"] >= (datetime.now()-timedelta(7)).isoformat()]
        return {"cost_7d": sum(r["cost"] for r in recent), "requests_7d": len(recent), "errors_7d": sum(1 for r in recent if not r["success"]), "model_usage": self.data.get("model_stats", {})}
    
    def show(self):
        s = self.stats()
        print(f"\n== LLM USAGE STATS ==")
        print(f"Cost (7d): ${s['cost_7d']:.4f}")
        print(f"Requests (7d): {s['requests_7d']}")
        print(f"Error Rate: {s['errors_7d']/max(s['requests_7d'],1)*100:.1f}%")
        print(f"\nMODEL USAGE:")
        for m, d in sorted(s["model_usage"].items(), key=lambda x: x[1]["requests"], reverse=True):
            sr = d["success"]/max(d["requests"],1)*100
            print(f"  {m:20} | {d['requests']:4} req | {sr:5.1f}%")


# ═══════════════════════════════════════════════════════════════
# 🎯 LLM ROUTER MAIN CLASS
# ═══════════════════════════════════════════════════════════════
class LLMRouter:
    def __init__(self):
        self.models = {m.name: m for m in MODEL_REGISTRY}
        self.tracker = UsageTracker()
        self.cache = SemanticCache()
        self.lb = LoadBalancer()
        self.load_keys()
    
    def load_keys(self):
        f = Path("/home/clawbot/.openclaw/workspace/.api_keys")
        if f.exists():
            for line in f.read_text().strip().split("\n"):
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ[k] = v
    
    def available(self):
        return [m for m in MODEL_REGISTRY if not m.api_key_env or os.environ.get(m.api_key_env)]
    
    def query(self, prompt, priority="balanced", use_cache=True, strategy="round_robin"):
        """
        Execute query with CACHING + LOAD BALANCING + FALLBACK.
        """
        # Check cache first
        if use_cache:
            cached = self.cache.get(prompt)
            if cached:
                return {"success": True, "response": cached, "model": "CACHE", "cached": True}
        
        # Get available models
        chain = FALLBACK_CHAINS.get(priority, FALLBACK_CHAINS["balanced"])
        available = self.available()
        
        # Select model using load balancer
        selected_models = [m for m in [self.models.get(n) for n in chain] if m and m in available]
        
        if not selected_models:
            return {"success": False, "error": "No models available"}
        
        for model in selected_models:
            m = self.lb.select(selected_models, strategy)
            print(f"  -> {m.name} ({m.provider})...", end=" ", flush=True)
            
            success, response, latency, cost = self._call(m, prompt)
            
            self.lb.record_latency(m.name, latency)
            
            if success:
                print(f"OK {latency}ms")
                self.tracker.record(m.name, m.provider, True, latency, cost)
                
                # Cache the response
                if use_cache:
                    self.cache.set(prompt, response)
                
                return {"success": True, "response": response, "model": m.name, "latency": latency, "cost": cost, "cached": False}
            
            print(f"FAIL - {response[:60]}")
            self.tracker.record(m.name, m.provider, False, latency, 0, response)
        
        return {"success": False, "error": "All models failed"}
    
    def _call(self, m, prompt):
        start = time.time()
        if m.provider == "Google": return self._gemini(m, prompt, start)
        elif m.provider == "OpenAI": return self._openai(m, prompt, start)
        elif m.provider == "Minimax": return self._minimax(m, prompt, start)
        elif m.provider == "OpenRouter": return self._openrouter(m, prompt, start)
        elif m.provider == "HuggingFace": return self._huggingface(m, prompt, start)
        elif m.provider == "Anthropic": return self._anthropic(m, prompt, start)
        return False, f"Unknown: {m.provider}", 0, 0
    
    def _gemini(self, m, prompt, start):
        import urllib.request, urllib.error
        try:
            key = os.environ.get("GEMINI_API_KEY","")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m.model_string}:generateContent?key={key}"
            data = json.dumps({"contents":[{"parts":[{"text":prompt}]}]}).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                result = json.loads(r.read())
                return True, result["candidates"][0]["content"]["parts"][0]["text"], int((time.time()-start)*1000), 0
        except Exception as e:
            return False, str(e), int((time.time()-start)*1000), 0
    
    def _openai(self, m, prompt, start):
        import urllib.request, urllib.error
        try:
            key = os.environ.get("OPENAI_API_KEY","")
            url = "https://api.openai.com/v1/chat/completions"
            data = json.dumps({"model":m.model_string,"messages":[{"role":"user","content":prompt}]}).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json","Authorization":f"Bearer {key}"})
            with urllib.request.urlopen(req, timeout=30) as r:
                result = json.loads(r.read())
                usage = result.get("usage",{})
                cost = (usage.get("prompt_tokens",0)*m.cost_per_1k_input + usage.get("completion_tokens",0)*m.cost_per_1k_output)/1000
                return True, result["choices"][0]["message"]["content"], int((time.time()-start)*1000), cost
        except Exception as e:
            return False, str(e), int((time.time()-start)*1000), 0
    
    def _openrouter(self, m, prompt, start):
        import urllib.request, urllib.error
        try:
            key = os.environ.get("OPENROUTER_API_KEY_2", os.environ.get("OPENROUTER_API_KEY",""))
            url = "https://openrouter.ai/api/v1/chat/completions"
            data = json.dumps({"model":m.model_string,"messages":[{"role":"user","content":prompt}]}).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json","Authorization":f"Bearer {key}"})
            with urllib.request.urlopen(req, timeout=30) as r:
                result = json.loads(r.read())
                return True, result["choices"][0]["message"]["content"], int((time.time()-start)*1000), 0
        except Exception as e:
            return False, str(e), int((time.time()-start)*1000), 0
    
    def _huggingface(self, m, prompt, start):
        import urllib.request, urllib.error
        try:
            key = os.environ.get("HUGGINGFACE_API_KEY","")
            url = f"https://api-inference.huggingface.co/models/{m.model_string}"
            data = json.dumps({"inputs":prompt}).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json","Authorization":f"Bearer {key}"})
            with urllib.request.urlopen(req, timeout=30) as r:
                result = json.loads(r.read())
                text = result[0].get("generated_text","") if isinstance(result, list) else result.get("generated_text","")
                return True, text, int((time.time()-start)*1000), 0
        except Exception as e:
            return False, str(e), int((time.time()-start)*1000), 0
    
    def _anthropic(self, m, prompt, start):
        import urllib.request, urllib.error
        try:
            key = os.environ.get("ANTHROPIC_API_KEY","")
            url = "https://api.anthropic.com/v1/messages"
            data = json.dumps({"model":m.model_string,"max_tokens":1024,"messages":[{"role":"user","content":prompt}]}).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json","x-api-key":key,"anthropic-version":"2023-06-01"})
            with urllib.request.urlopen(req, timeout=30) as r:
                result = json.loads(r.read())
                usage = result.get("usage",{})
                cost = (usage.get("input_tokens",0)*m.cost_per_1k_input + usage.get("output_tokens",0)*m.cost_per_1k_output)/1000
                return True, result["content"][0]["text"], int((time.time()-start)*1000), cost
        except Exception as e:
            return False, str(e), int((time.time()-start)*1000), 0
    
    def _minimax(self, m, prompt, start):
        import urllib.request, urllib.error
        try:
            key = os.environ.get("MINIMAX_API_KEY","")
            url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
            data = json.dumps({"model":m.model_string,"messages":[{"role":"user","content":prompt}]}).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json","Authorization":f"Bearer {key}"})
            with urllib.request.urlopen(req, timeout=30) as r:
                result = json.loads(r.read())
                return True, result["choices"][0]["message"]["content"], int((time.time()-start)*1000), 0
        except Exception as e:
            return False, str(e), int((time.time()-start)*1000), 0
    
    def show_cache_stats(self):
        s = self.cache.stats()
        print(f"""
== CACHE STATS ==
Hits:     {s['hits']}
Misses:   {s['misses']}
Hit Rate: {s['hit_rate']:.1f}%
Entries:  {s['entries']}
Saved:    ${s['saved_cost']:.6f}
""")
    
    def show_load_balancer_stats(self):
        s = self.lb.stats()
        print(f"""
== LOAD BALANCER STATS ==
Strategy: round_robin
""")
        print("MODEL USAGE:")
        for m, count in sorted(s["usage"].items(), key=lambda x: x[1], reverse=True):
            avg_lat = s["avg_latency"].get(m, 0)
            print(f"  {m:20} | {count:4} uses | {avg_lat:6.0f}ms avg")


if __name__ == "__main__":
    import urllib.request, urllib.error
    p = argparse.ArgumentParser(description="LLM Router v5.0 - Caching + Load Balancing")
    p.add_argument("--query","-q",help="Query to execute")
    p.add_argument("--priority","-p",default="balanced",choices=["speed","quality","cost","balanced"])
    p.add_argument("--no-cache",action="store_true",help="Disable cache")
    p.add_argument("--strategy","-s",default="round_robin",choices=["round_robin","least_used","fastest_avg","weighted"],help="Load balancing strategy")
    p.add_argument("--list","-l",action="store_true")
    p.add_argument("--stats",action="store_true")
    p.add_argument("--cache-stats",action="store_true")
    p.add_argument("--lb-stats",action="store_true")
    args = p.parse_args()
    
    router = LLMRouter()
    
    if args.cache_stats:
        router.show_cache_stats()
    elif args.lb_stats:
        router.show_load_balancer_stats()
    elif args.stats:
        router.tracker.show()
    elif args.list:
        for m in MODEL_REGISTRY:
            ok = m.api_key_env and os.environ.get(m.api_key_env)
            s = "OK" if ok else "--"
            cost = "FREE" if m.is_free else f"${m.cost_per_1k_input}"
            print(f"[{s}] {m.name:25} | {m.provider:12} | S{m.speed_score} Q{m.quality_score} | {cost}")
    elif args.query:
        print(f"\nQuery: {args.query[:50]}...\n")
        result = router.query(args.query, args.priority, use_cache=not args.no_cache, strategy=args.strategy)
        if result["success"]:
            tag = " [CACHED]" if result.get("cached") else ""
            print(f"\nSUCCESS using {result['model']}{tag}")
            lat = result.get('latency', 0); cost = result.get('cost', 0); print(f"Latency: {lat}ms | Cost: ${cost:.6f}")
            print(f"\nResponse:\n{result['response'][:300]}")
        else:
            print(f"\nFAILED: {result['error']}")
    else:
        print("LLM Router v5.0 - Smart Caching + Load Balancing")
        print("  --query/-q <text>     Execute query")
        print("  --priority/-p        speed|quality|cost|balanced")
        print("  --strategy/-s        round_robin|least_used|fastest_avg|weighted")
        print("  --no-cache           Disable cache")
        print("  --stats/-s           Show usage stats")
        print("  --cache-stats         Show cache stats")
        print("  --lb-stats           Show load balancer stats")
