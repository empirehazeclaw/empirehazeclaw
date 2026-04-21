"""Learning Loop v3 — Modularized Structure

This module contains the complete learning loop system.
Split from monolith for better maintainability.
"""

from .state.manager import load_state, save_state
from .patterns.matcher import PatternMatcher
from .validation.gate import ValidationGate

__all__ = [
    'load_state', 'save_state',
    'PatternMatcher', 
    'ValidationGate',
]
