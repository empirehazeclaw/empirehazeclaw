#!/usr/bin/env python3
"""
🎭 HUMANIZER + HUMOR INJECTOR
============================
Makes content sound more human and adds wit!
"""

import re
import random

# AI patterns to remove
AI_PATTERNS = [
    (r'\b moreover\b', 'And'),
    (r'\b furthermore\b', 'Also'),
    (r'\b consequently\b', 'So'),
    (r'\b additionally\b', 'And'),
    (r'\b in conclusion\b', 'Anyway'),
    (r'\b it is important to note that\b', ''),
    (r'\b one can observe that\b', ''),
    (r'\b it is worth mentioning\b', ''),
    (r'\b as previously mentioned\b', ''),
    (r'\b significantly\b', 'really'),
    (r'\b essentially\b', 'basically'),
    (r'\b fundamentally\b', ''),
    (r'—', '-'),
    (r'\.{3,}', '...'),
]

# Humor injections
HUMOR_INJECTIONS = [
    " (Cue awkward silence)",
    " *Chef's kiss*",
    " Don't tell my manager.",
    " This is the part where I pretend to be confident.",
    " Spoiler: It didn't work.",
    " Plot twist: It was free.",
    " At least my plants don't judge me.",
    " My keyboard isn't judge-y. Oh wait, it auto-corrects.",
    " That's what she said. (Just kidding. Or am I?)",
    " 10/10 would recommend to my future self.",
    " Don't @ me.",
    " I am legally required to say this worked in testing.",
    " Side effects may include: actually finishing this.",
    " Your move, universe.",
]

def humanize(text):
    """Remove AI patterns"""
    for pattern, replacement in AI_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text

def add_humor(text, intensity="medium"):
    """Add humor to text"""
    # Random placement
    if random.random() > 0.7:  # 30% chance
        injection = random.choice(HUMOR_INJECTIONS)
        
        # Add at end or middle
        if random.random() > 0.5:
            text += injection
        else:
            sentences = text.split('. ')
            if len(sentences) > 1:
                mid = len(sentences) // 2
                sentences.insert(mid, injection.replace('(', '').replace(')', ''))
                text = '. '.join(sentences)
    
    return text

def process_text(text, add_wit=True):
    """Full humanization"""
    # Step 1: Remove AI patterns
    text = humanize(text)
    
    # Step 2: Add humor if requested
    if add_wit:
        text = add_humor(text)
    
    return text

if __name__ == "__main__":
    # Test
    test = "Moreover, this is essentially important. Furthermore, we can observe that fundamentally this is significant."
    
    print("Original:")
    print(test)
    print("\nHumanized + Wit:")
    print(process_text(test))

# English humor for tweets
ENGLISH_HUMOR = [
    " This is why we can't have nice things.",
    " Worked in testing. Your results may vary.",
    " Don't @ me.",
    " I am legally required to say this worked in testing.",
    " Side effects may include: actually finishing this.",
    " Your move, universe.",
    " Plot twist: It was free.",
    " 10/10 would recommend.",
    " Spoiler: It didn't work.",
    " That's what she said. (Just kidding. Or am I?)",
]
