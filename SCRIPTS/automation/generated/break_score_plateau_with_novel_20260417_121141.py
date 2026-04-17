#!/usr/bin/env python3
"""
Score Plateau Breaker - A simulation of breaking score stagnation
with novel approaches and adaptive learning strategies.
"""

import random
import time
import math
from enum import Enum
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


class PlateauPhase(Enum):
    """Stages of a score plateau."""
    STABLE = "stable"
    DETECTED = "detected"
    STRUGGLING = "strugging"
    BREAKTHROUGH = "breakthrough"
    NEW_LEVEL = "new_level"


@dataclass
class ScoreRecord:
    """Single score record with metadata."""
    timestamp: float
    score: float
    method: str
    effort: float
    
    def __repr__(self):
        return f"ScoreRecord(score={self.score:.2f}, method='{self.method}')"


@dataclass
class PlateauInfo:
    """Information about a detected plateau."""
    start_score: float
    duration: int
    attempts: int
    phase: PlateauPhase
    methods_tried: List[str] = field(default_factory=list)
    
    def __repr__(self):
        return f"PlateauInfo(score={self.start_score:.2f}, duration={self.duration}, phase={self.phase.value})"


class Strategy(ABC):
    """Abstract base class for breakthrough strategies."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, context: Dict) -> Tuple[float, float]:
        """Execute strategy and return (score_gain, effort)."""
        pass
    
    def __repr__(self):
        return f"Strategy({self.name})"


class RandomExploration(Strategy):
    """Random exploration to discover new patterns."""
    
    def __init__(self):
        super().__init__("Random Exploration", "Try random approaches to find hidden patterns")
    
    def execute(self, context: Dict) -> Tuple[float, float]:
        time.sleep(0.01)  # Simulate thinking
        discovery_bonus = random.uniform(0.5, 2.5)
        success_rate = random.random()
        
        if success_rate > 0.3:
            gain = context.get('base_gain', 5) * discovery_bonus
            effort = random.uniform(1.5, 3.0)
            return gain, effort
        else:
            return random.uniform(0.5, 2.0), random.uniform(0.5, 1.5)


class MomentumShift(Strategy):
    """Shift from current approach dramatically."""
    
    def __init__(self):
        super().__init__("Momentum Shift", "Change velocity and direction completely")
    
    def execute(self, context: Dict) -> Tuple[float, float]:
        time.sleep(0.02)
        plateau_duration = context.get('plateau_duration', 1)
        intensity = min(plateau_duration * 0.3, 2.0)
        
        success_chance = 0.4 + (intensity * 0.1)
        if random.random() < success_chance:
            base = context.get('base_gain', 5)
            return base * (1.5 + intensity), 2.5 + intensity
        return random.uniform(1.0, 3.0), 1.8


class DeepFocus(Strategy):
    """Intensive focus on weak areas."""
    
    def __init__(self):
        super().__init__("Deep Focus", "Concentrate deeply on problem areas")
    
    def execute(self, context: Dict) -> Tuple[float, float]:
        time.sleep(0.025)
        weak_areas = context.get('weak_areas', 3)
        focus_power = math.log(weak_areas + 1) * random.uniform(1.5, 3.0)
        
        if random.random() < 0.6:
            return context.get('base_gain', 5) * focus_power, 3.0
        return random.uniform(2.0, 4.0), 2.5


class CrossTraining(Strategy):
    """Apply techniques from different domains."""
    
    def __init__(self):
        super().__init__("Cross Training", "Borrow techniques from other fields")
    
    def execute(self, context: Dict) -> Tuple[float, float]:
        time.sleep(0.015)
        domains = context.get('known_domains', ['general'])
        domain = random.choice(domains + ['creative', 'logical', 'intuitive'])
        
        synergy = random.uniform(1.2, 2.8)
        if random.random() < 0.55:
            return context.get('base_gain', 5) * synergy, 2.2
        return random.uniform(1.5, 3.5), 1.8


class IncrementalChallenge(Strategy):
    """Gradually increase difficulty in small steps."""
    
    def __init__(self):
        super().__init__("Incremental Challenge", "Step up difficulty gradually")
    
    def execute(self, context: Dict) -> Tuple[float, float]:
        time.sleep(0.018)
        step = context.get('current_step', 0.1)
        progress = context.get('progress_meter', 0.5)
        
        if progress > 0.7:
            return context.get('base_gain', 5) * 1.8, 1.5
        return context.get('base_gain', 5) * 1.2, 1.2


class RestAndRecovery(Strategy):
    """Take a break and let subconscious work."""
    
    def __init__(self):
        super().__init__("Rest & Recovery", "Rest to allow subconscious processing")
    
    def execute(self, context: Dict) -> Tuple[float, float]:
        time.sleep(0.03)
        rest_quality = random.uniform(0.3, 1.0)
        
        if random.random() < 0.7:
            return context.get('base_gain', 5) * rest_quality * 2.0, 0.5
        return random.uniform(0.5, 1.5), 0.3


class MilestoneTargeting(Strategy):
    """Target specific milestone scores."""
    
    def __init__(self):
        super().__init__("Milestone Targeting", "Aim for specific milestone targets")
    
    def execute(self, context: Dict) -> Tuple[float, float]:
        time.sleep(0.012)
        current = context.get('current_score', 0)
        milestone = context.get('next_milestone', 100)
        distance = abs(milestone - current)
        
        if distance < 10 and random.random() < 0.65:
            return context.get('base_gain', 5) * 2.5, 2.0
        return context.get('base_gain', 5) * 1.3, 1.5


class AdaptiveLearning(Strategy):
    """Learn from previous attempts and adapt."""
    
    def __init__(self):
        super().__init__("Adaptive Learning", "Learn from history and adapt approach")
        self.memory: List[Dict] = []
    
    def execute(self, context: Dict) -> Tuple[float, float]:
        time.sleep(0.02)
        
        if self.memory:
            successful = [m for m in self.memory if m.get('success', False)]
            if successful:
                bonus = len(successful) * 0.1
                if random.random() < 0.7 + bonus * 0.1:
                    return context.get('base_gain', 5) * (1.5 + bonus), 2.0
        
        self.memory.append({
            'context': context,
            'success': random.random() > 0.4
        })
        return random.uniform(1.5, 4.0), 1.8
    
    def reset_memory(self):
        self.memory = []


class BreakthroughMomentum(Strategy):
    """Build cumulative momentum for breakthrough."""
    
    def __init__(self):
        super().__init__("Breakthrough Momentum", "Build up momentum for explosive progress")
        self.momentum = 0.0
    
    def execute(self, context: Dict) -> Tuple[float, float]:
        time.sleep(0.015)
        self.momentum = min(self.momentum + 0.15, 2.0)
        
        if self.momentum >= 1.5 and random.random() < 0.75:
            self.momentum = 0.0
            return context.get('base_gain', 5) * 3.5, 3.5
        
        self.momentum += 0.1
        return context.get('base_gain', 5) * (0.8 + self.momentum), 1.0 + self.momentum
    
    def reset_momentum(self):
        self.momentum = 0.0


class PlateauBreaker:
    """Main class for breaking score plateaus."""
    
    STRATEGIES = [
        RandomExploration(),
        MomentumShift(),
        DeepFocus(),
        CrossTraining(),
        IncrementalChallenge(),
        RestAndRecovery(),
        MilestoneTargeting(),
        AdaptiveLearning(),
        BreakthroughMomentum()
    ]
    
    def __init__(self, name: str = "Player"):
        self.name = name
        self.score = 0.0
        self.history: List[ScoreRecord] = []
        self.plateau_info: Optional[PlateauInfo] = None
        self.milestones = [100, 200, 500, 1000, 2000, 5000, 10000]
        self.current_milestone_index = 0
        
        self.stats = {
            'total_attempts': 0,
            'successful_breaks': 0,
            'strategies_used': {},
            'plateaus_encountered': 0
        }
    
    def get_next_milestone(self) -> float:
        """Get the next milestone to reach."""
        for i, m in enumerate(self.milestones):
            if self.score < m:
                return m
        return self.milestones[-1] * 2
    
    def detect_plateau(self) -> Optional[PlateauInfo]:
        """Detect if player is stuck in a plateau."""
        if len(self.history) < 5:
            return None
        
        recent = self.history[-5:]
        scores = [r.score for r in recent]
        
        min_score = min(scores)
        max_score = max(scores)
        variance = max_score - min_score
        
        if variance < 3.0:
            if self.plateau_info is None:
                self.plateau_info = PlateauInfo(
                    start_score=self.score,
                    duration=1,
                    attempts=0,
                    phase=PlateauPhase.DETECTED
                )
                self.stats['plateaus_encountered'] += 1
            else:
                self.plateau_info.duration += 1
            
            if self.plateau_info.duration >= 3:
                self.plateau_info.phase = PlateauPhase.STRUGGLING
            
            return self.plateau_info
        
        if self.plateau_info is not None:
            self.plateau_info.phase = PlateauPhase.BREAKTHROUGH
            self.stats['successful_breaks'] += 1
            self.plateau_info = None
        
        return None
    
    def build_context(self) -> Dict:
        """Build context dictionary for strategy execution."""
        recent_gains = []
        if len(self.history) >= 2:
            for i in range(len(self.history) - 1, max(0, len(self.history) - 5), -1):
                gain = self.history[i].score - self.history[i-1].score
                recent_gains.append(gain)
        
        base_gain = 5.0 if not recent_gains else max(1.0, sum(recent_gains) / len(recent_gains) * 0.5)
        
        return {
            'base_gain': base_gain,
            'plateau_duration': self.plateau_info.duration if self.plateau_info else 0,
            'weak_areas': random.randint(1, 5),
            'known_domains': ['general', 'technical', 'creative'],
            'current_step': random.uniform(0.05, 0.3),
            'progress_meter': min(1.0, self.score / max(1, self.get_next_milestone())),
            'current_score': self.score,
            'next_milestone': self.get_next_milestone(),
            'history_length': len(self.history)
        }
    
    def select_strategy(self) -> Strategy:
        """Select the best strategy based on situation."""
        if self.plateau_info is None:
            return random.choice(self.STRATEGIES[:5])
        
        plateau_phase = self.plateau_info.phase
        duration = self.plateau_info.duration
        
        if plateau_phase == PlateauPhase.STRUGGLING:
            if duration > 5:
                return self.STRATEGIES[8]  # Breakthrough Momentum
            elif duration > 3:
                return random.choice([self.STRATEGIES[1], self.STRATEGIES[7]])  # Momentum or Adaptive
            else:
                return random.choice([self.STRATEGIES[2], self.STRATEGIES[3]])  # Deep Focus or Cross Training
        elif plateau_phase == PlateauPhase.DETECTED:
            return random.choice([self.STRATEGIES[4], self.STRATEGIES[5], self.STRATEGIES[6]])
        else:
            return self.STRATEGIES[0]
    
    def apply_strategy(self) -> ScoreRecord:
        """Apply a strategy and record the result."""
        self.stats['total_attempts'] += 1
        
        strategy = self.select_strategy()
        
        if self.plateau_info:
            self.plateau_info.attempts += 1
            if strategy.name not in self.plateau_info.methods_tried:
                self.plateau_info.methods_tried.append(strategy.name)
        
        context = self.build_context()
        
        try:
            score_gain, effort = strategy.execute(context)
        except Exception as e:
            print(f"Strategy execution error: {e}")
            score_gain, effort = 1.0, 1.0
        
        self.score += score_gain
        
        record = ScoreRecord(
            timestamp=time.time(),
            score=self.score,
            method=strategy.name,
            effort=effort
        )
        self.history.append(record)
        
        self.stats['strategies_used'][strategy.name] = \
            self.stats['strategies_used'].get(strategy.name, 0) + 1
        
        return record
    
    def get_progress_report(self) -> str:
        """Generate a progress report."""
        next_milestone = self.get_next_milestone()
        progress_pct = (self.score / next_milestone) * 100 if next_milestone > 0 else 0
        
        lines = [
            f"\n{'='*50}",
            f"Player: {self.name}",
            f"Current Score: {self.score:.2f}",
            f"Next Milestone: {next_milestone:.2f} ({progress_pct:.1f}% progress)",
            f"Total Attempts: {self.stats['total_attempts']}",
            f"Plateaus Encountered: {self.stats['plateaus_encountered']}",
            f"Successful Breaks: {self.stats['successful_breaks']}",
            f"History Entries: {len(self.history)}"
        ]
        
        if self.plateau_info:
            lines.append(f"Current Plateau: {self.plateau_info.duration} rounds, Phase: {self.plateau_info.phase.value}")
            lines.append(f"Strategies Tried: {', '.join(self.plateau_info.methods_tried)}")
        
        if self.stats['strategies_used']:
            lines.append("\nStrategy Usage:")
            for strategy, count in sorted(self.stats['strategies_used'].items(), key=lambda x: -x[1]):
                lines.append(f"  - {strategy}: {count}x")
        
        lines.append(f"{'='*50}\n")
        return "\n".join(lines)
    
    def display_recent_history(self, count: int = 10):
        """Display recent score history."""
        print(f"\n--- Recent History (last {min(count, len(self.history))} entries) ---")
        start = max(0, len(self.history) - count)
        for record in self.history[start:]:
            print(f"  {record}")
        print()


def run_simulation(player_name: str = "Champion", target_score: float = 2500, 
                   max_rounds: int = 200, verbose: bool = True):
    """
    Run a simulation of breaking score plateaus.
    
    Args:
        player_name: Name of the player
        target_score: Score to reach for victory
        max_rounds: Maximum number of rounds to simulate
        verbose: Whether to print detailed progress
    """
    print(f"\n{'#'*60}")
    print(f"# SCORE PLATEAU BREAKER - {player_name}")
    print(f"# Target: {target_score}, Max Rounds: {max_rounds}")
    print(f"{'#'*60}\n")
    
    breaker = PlateauBreaker(player_name)
    
    round_num = 0
    last_report_round = 0
    
    try:
        while round_num < max_rounds:
            round_num += 1
            
            plateau = breaker.detect_plateau()
            record = breaker.apply_strategy()
            
            if verbose and round_num % 10 == 0:
                status = "PLATEAU!" if plateau else "Progress"
                print(f"Round {round_num:3d}: Score={breaker.score:8.2f} | "
                      f"Method={record.method:25s} | {status}")
            
            if breaker.score >= target_score:
                print(f"\n*** VICTORY! {player_name} reached {breaker.score:.2f} in {round_num} rounds! ***\n")
                break
            
            if plateau and plateau.phase == PlateauPhase.STRUGGLING and plateau.duration > 8:
                print(f"\n[WARNING] {player_name} stuck in extended plateau at {breaker.score:.2f}")