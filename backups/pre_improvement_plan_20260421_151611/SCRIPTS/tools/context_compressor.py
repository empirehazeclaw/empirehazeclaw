#!/usr/bin/env python3
"""
context_compressor.py — Context Compression for Token Limit Errors
================================================================
For when context window is exhausted (token limit exceeded).

Strategy:
1. Detect context overflow
2. Extract critical information (decisions, facts, todos)
3. Generate summary of conversation
4. Retain only critical info for next turn
5. Continue with compressed context

Usage:
    from context_compressor import compress_context, extract_critical_info
    
    compressed = compress_context(conversation_history)
"""

import re
from typing import List, Dict, Tuple
from datetime import datetime

# Critical patterns that should ALWAYS be preserved
CRITICAL_PATTERNS = [
    # Decisions
    r"(?i)(decided?|decision|agreed?|choice|chose|selected)",
    r"(?i)(we will|going to|must|should|need to|have to)",
    r"(?i)(TODO|FIXME|ACTION|IMPORTANT|NOTE:)",
    
    # Facts & Data
    r"(?i)(fact:|data:|result:|found|discovered|learned)",
    r"(?i)(metric|statistic|number|percentage|count)",
    
    # User preferences
    r"(?i)(prefer|preference|wants|wants to|likes|asked for)",
    r"(?i)(don't|do not|never|always|从来不|绝不)",
    
    # Commitments
    r"(?i)(promised|committed|will do|guarantee|assured)",
    r"(?i)(deliver|send|report|create|build|make|fix)",
    
    # Errors & Problems
    r"(?i)(error|failed|issue|problem|bug|broken)",
    r"(?i)(not working|doesn't work|won't|cannot|couldn't)",
]

# Patterns that can be COMPRESSED or removed
COMPRESSIBLE_PATTERNS = [
    # Greetings
    r"(?i)(hi|hello|hey|greetings|how are you)",
    # Casual conversation
    r"(?i)(thanks|thank you|please|okay|ok|great|nice|sounds good)",
    # Repetitive confirmations
    r"(?i)(yes|yeah|yep|no|nope|correct|right)",
    # Meta-comments
    r"(?i)(as I said|like I mentioned|I mentioned earlier)",
]


def extract_critical_info(messages: List[Dict]) -> Dict:
    """
    Extract critical information from conversation.
    
    Returns:
        {
            "decisions": [...],
            "facts": [...],
            "todos": [...],
            "preferences": [...],
            "errors": [...]
        }
    """
    result = {
        "decisions": [],
        "facts": [],
        "todos": [],
        "preferences": [],
        "errors": []
    }
    
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        
        if not content:
            continue
        
        # Check for decisions
        for pattern in CRITICAL_PATTERNS[:2]:  # Decision patterns
            if re.search(pattern, content):
                result["decisions"].append({
                    "role": role,
                    "content": content[:500],  # Truncate
                    "timestamp": msg.get("timestamp", "")
                })
                break
        
        # Check for TODOs
        if re.search(r"(?i)(TODO|FIXME|ACTION|action:)", content):
            result["todos"].append({
                "role": role,
                "content": content[:500],
                "timestamp": msg.get("timestamp", "")
            })
        
        # Check for errors
        if re.search(r"(?i)(error|failed|exception)", content):
            result["errors"].append({
                "role": role,
                "content": content[:500],
                "timestamp": msg.get("timestamp", "")
            })
        
        # Check for preferences (user only)
        if role == "user":
            for pattern in CRITICAL_PATTERNS[4:6]:  # Preference patterns
                if re.search(pattern, content):
                    result["preferences"].append({
                        "content": content[:500],
                        "timestamp": msg.get("timestamp", "")
                    })
                    break
    
    return result


def compress_context(messages: List[Dict], max_messages: int = 10) -> List[Dict]:
    """
    Compress conversation context to fit within token limit.
    
    Strategy:
    1. Keep first message (system prompt)
    2. Extract critical info from middle messages
    3. Keep last N messages (recent context)
    4. Add summary of compressed info
    
    Args:
        messages: List of message dicts
        max_messages: Maximum messages to keep in compressed context
    
    Returns:
        Compressed message list
    """
    if len(messages) <= max_messages:
        return messages
    
    # Always keep system prompt (first message)
    system_msg = messages[0] if messages else {}
    
    # Get critical info from all messages
    critical = extract_critical_info(messages[1:])  # Exclude system
    
    # Keep last N messages (most recent context)
    recent = messages[-(max_messages - 1):] if len(messages) > max_messages - 1 else messages[1:]
    
    # Build compressed context
    compressed = []
    
    # 1. System prompt
    if system_msg:
        compressed.append(system_msg)
    
    # 2. Summary of compressed info
    summary_parts = []
    
    if critical["decisions"]:
        summary_parts.append("## Key Decisions:\n")
        for d in critical["decisions"][:5]:  # Max 5
            summary_parts.append("- [%s]: %s...\n" % (d['role'], d['content'][:200]))
    
    if critical["todos"]:
        summary_parts.append("\n## TODOs:\n")
        for t in critical["todos"][:5]:
            summary_parts.append("- %s...\n" % (t['content'][:200]))
    
    if critical["errors"]:
        summary_parts.append("\n## Errors:\n")
        for e in critical["errors"][:3]:
            summary_parts.append("- %s...\n" % (e['content'][:200]))
    
    if critical["preferences"]:
        summary_parts.append("\n## User Preferences:\n")
        for p in critical["preferences"][:3]:
            summary_parts.append("- %s...\n" % (p['content'][:200]))
    
    # Add summary as a system message
    if summary_parts:
        summary_text = "".join(summary_parts)
        compressed.append({
            "role": "system",
            "content": "[COMPRESSED CONTEXT - Previous conversation summarized]\n%s" % summary_text,
            "timestamp": datetime.now().isoformat()
        })
    
    # 3. Add recent messages (with full content)
    compressed.extend(recent)
    
    return compressed


def estimate_tokens(text: str) -> int:
    """
    Rough estimation of token count.
    Rule of thumb: ~4 chars per token for English.
    """
    return len(text) // 4


def needs_compression(messages: List[Dict], token_limit: int = 150000) -> Tuple[bool, int]:
    """
    Check if context needs compression.
    
    Returns:
        (needs_compression, estimated_tokens)
    """
    total_chars = sum(len(m.get("content", "")) for m in messages)
    estimated_tokens = total_chars // 4
    
    return estimated_tokens > token_limit * 0.8, estimated_tokens


def smart_compress(messages: List[Dict], token_limit: int = 150000) -> List[Dict]:
    """
    Smart context compression that decides best strategy.
    
    Strategies:
    1. If over 80% of limit: Light compression (remove greetings, casual)
    2. If over 90% of limit: Medium compression (summarize middle)
    3. If over 100% of limit: Heavy compression (aggressive summarize)
    """
    needs_compress, tokens = needs_compression(messages, token_limit)
    
    if not needs_compress:
        return messages
    
    ratio = tokens / token_limit
    
    if ratio > 1.0:
        # Heavy compression
        return compress_context(messages, max_messages=6)
    elif ratio > 0.9:
        # Medium compression
        return compress_context(messages, max_messages=10)
    else:
        # Light compression - just remove greetings
        return light_compress(messages)


def light_compress(messages: List[Dict]) -> List[Dict]:
    """
    Light compression - remove greetings and casual conversation only.
    """
    compressed = []
    
    for msg in messages:
        content = msg.get("content", "")
        
        # Check if it's all compressible patterns
        is_compressible = True
        for pattern in COMPRESSIBLE_PATTERNS:
            if re.search(pattern, content):
                is_compressible = False
                break
        
        if is_compressible:
            # Still add but content might be empty - skip empty ones
            if content.strip():
                compressed.append(msg)
        else:
            compressed.append(msg)
    
    return compressed


# ============ CLI Interface ============

if __name__ == "__main__":
    print("Context Compressor - Token Limit Error Handler")
    print("=" * 50)
    print()
    print("Usage:")
    print("  from context_compressor import compress_context, smart_compress")
    print()
    print("Strategies:")
    print("  - Light:  Remove greetings/casual (>80% limit)")
    print("  - Medium: Summarize middle messages (>90% limit)")
    print("  - Heavy:  Aggressive compression (>100% limit)")
    print()
    print("Critical Info Preserved:")
    print("  - Decisions")
    print("  - TODOs")
    print("  - User Preferences")
    print("  - Errors/Problems")
    print("  - Recent messages")
