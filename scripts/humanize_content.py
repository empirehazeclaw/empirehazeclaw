#!/usr/bin/env python3
"""
Humanize Content - Makes AI-generated text sound more human/natural
Uses linguistic patterns to add variance and reduce AI-detection markers
"""
import re
import random
from typing import List

class Humanizer:
    def __init__(self):
        # Contraction mappings (formal -> informal)
        self.contractions = {
            "does not": "doesn't",
            "do not": "don't",
            "will not": "won't",
            "cannot": "can't",
            "would not": "wouldn't",
            "should not": "shouldn't",
            "could not": "couldn't",
            "it is": "it's",
            "that is": "that's",
            "there is": "there's",
            "we are": "we're",
            "you are": "you're",
            "they are": "they're",
            "I am": "I'm",
            "have not": "haven't",
            "has not": "hasn't",
            "had not": "hadn't",
        }
        
        # Sentence starters for variety
        self.starters = [
            "Actually,", "Well,", "So,", "Here's the thing:", 
            "You know,", "Honestly,", "Look,", "Right,", 
            "Basically,", "The thing is,", "I mean,", "Sure,", "Look,"
        ]
        
        # Filler words
        self.fillers = [" honestly,", " actually,", " really,", " basically,", " like,"]
    
    def add_contractions(self, text: str) -> str:
        """Convert formal to informal where appropriate"""
        for formal, informal in self.contractions.items():
            # Only replace whole words
            text = re.sub(r'\b' + formal + r'\b', informal, text, flags=re.IGNORECASE)
        return text
    
    def vary_sentence_starters(self, text: str) -> str:
        """Add variety to sentence beginnings"""
        sentences = re.split(r'([.!?]+)', text)
        result = []
        
        for i, part in enumerate(sentences):
            if i % 2 == 0 and part.strip() and len(part) > 10:
                # 30% chance to add a starter
                if random.random() < 0.3:
                    starter = random.choice(self.starters)
                    part = starter + " " + part.strip().lower()
            result.append(part)
        
        return ''.join(result)
    
    def add_hesitations(self, text: str) -> str:
        """Add natural hesitations"""
        words = text.split()
        result = []
        
        for word in words:
            result.append(word)
            # 5% chance of filler after word
            if random.random() < 0.05 and len(result) > 3:
                result.append(random.choice(self.fillers).lstrip())
        
        return ' '.join(result)
    
    def add_paragraph_breaks(self, text: str) -> str:
        """Add natural paragraph breaks"""
        # Split long paragraphs
        paragraphs = text.split('\n\n')
        result = []
        
        for p in paragraphs:
            if len(p) > 500:
                # Split long paragraphs
                sentences = re.split(r'(?<=[.!?])\s+', p)
                new_paras = []
                current = []
                current_len = 0
                
                for s in sentences:
                    current.append(s)
                    current_len += len(s)
                    if current_len > 250:
                        new_paras.append(' '.join(current))
                        current = []
                        current_len = 0
                
                if current:
                    new_paras.append(' '.join(current))
                
                result.append('\n\n'.join(new_paras))
            else:
                result.append(p)
        
        return '\n\n'.join(result)
    
    def humanize(self, text: str, level: str = "medium") -> str:
        """
        Humanize text to make it sound more natural
        
        Levels:
        - light: Just subtle changes
        - medium: Contractions + sentence starters
        - heavy: All transformations
        """
        if level == "light":
            text = self.add_contractions(text)
        elif level == "medium":
            text = self.add_contractions(text)
            text = self.vary_sentence_starters(text)
        else:  # heavy
            text = self.add_contractions(text)
            text = self.vary_sentence_starters(text)
            text = self.add_hesitations(text)
            text = self.add_paragraph_breaks(text)
        
        return text

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: humanize_content.py <text> [level]")
        print("Levels: light, medium, heavy")
        return
    
    text = sys.argv[1]
    level = sys.argv[2] if len(sys.argv) > 2 else "medium"
    
    h = Humanizer()
    result = h.humanize(text, level)
    
    print(result)

if __name__ == "__main__":
    main()
