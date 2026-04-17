#!/usr/bin/env python3
"""
graceful_degradation.py — Graceful Degradation Pattern
====================================================
For cascade failures: instead of complete shutdown, continue with reduced functionality.

Strategy:
1. Detect cascade failure
2. Identify which components are failing
3. Disable non-essential features
4. Keep core functionality running
5. Enter maintenance mode
6. Auto-recover when issue is resolved

Usage:
    from graceful_degradation import GracefulDegradation, degradation_manager
    
    # When a component fails:
    degradation_manager.mark_component_failure("email")
    
    # Check what's degraded:
    status = degradation_manager.get_degradation_status()
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

class DegradationLevel(Enum):
    """Degradation levels from best to worst."""
    NOMINAL = "nominal"           # All systems operational
    LIGHT = "light"               # Minor issues, reduced performance
    MODERATE = "moderate"         # Some features disabled
    SEVERE = "severe"            # Only core functionality
    EMERGENCY = "emergency"       # Minimal functionality
    DOWN = "down"                 # Complete failure


# Component priorities (lower = more essential)
COMPONENT_PRIORITIES = {
    "gateway": 1,           # CRITICAL - core gateway
    "cron": 2,              # CRITICAL - scheduled jobs
    "memory": 3,            # CRITICAL - memory systems
    "messaging": 4,         # IMPORTANT - messaging
    "healer": 5,            # IMPORTANT - self-healing
    "kg": 6,                # IMPORTANT - knowledge graph
    "skills": 7,            # USEFUL - skills
    "analytics": 8,          # NICE-TO-HAVE - analytics
    "backup": 9,            # NICE-TO-HAVE - backups
    "non-essential": 10,     # CAN BE DISABLED
}

# Features available at each degradation level
DEGRADATION_FEATURES: Dict[DegradationLevel, List[str]] = {
    DegradationLevel.NOMINAL: [
        "gateway", "cron", "memory", "messaging", "healer", 
        "kg", "skills", "analytics", "backup"
    ],
    DegradationLevel.LIGHT: [
        "gateway", "cron", "memory", "messaging", "healer", 
        "kg", "skills"
    ],
    DegradationLevel.MODERATE: [
        "gateway", "cron", "memory", "messaging", "healer"
    ],
    DegradationLevel.SEVERE: [
        "gateway", "cron", "memory", "messaging"
    ],
    DegradationLevel.EMERGENCY: [
        "gateway", "memory"
    ],
    DegradationLevel.DOWN: [
        "gateway"
    ],
}


@dataclass
class ComponentStatus:
    """Status of a single component."""
    name: str
    healthy: bool = True
    failures: int = 0
    last_failure: Optional[str] = None
    degradation_allowed: bool = True
    auto_recover: bool = True
    recovery_timeout: int = 300  # seconds


@dataclass
class DegradationState:
    """Current degradation state."""
    level: DegradationLevel = DegradationLevel.NOMINAL
    active_components: Set[str] = field(default_factory=set)
    failed_components: Set[str] = field(default_factory=set)
    degraded_at: Optional[str] = None
    last_update: Optional[str] = None
    maintenance_mode: bool = False
    message: str = "All systems operational"


class GracefulDegradation:
    """
    Graceful Degradation Manager.
    
    Manages system degradation when cascade failures occur.
    Instead of complete shutdown, disables non-essential features.
    
    Usage:
        gd = GracefulDegradation()
        gd.mark_component_failure("analytics")
        status = gd.get_degradation_status()
    """
    
    def __init__(self, state_file: Optional[str] = None):
        self.state_file = state_file
        self.components: Dict[str, ComponentStatus] = {}
        self.state = DegradationState()
        
        # Initialize all known components
        for comp_name in COMPONENT_PRIORITIES.keys():
            self.components[comp_name] = ComponentStatus(name=comp_name)
        
        # Load state if exists
        self._load_state()
    
    def mark_component_failure(
        self, 
        component: str, 
        error: Optional[str] = None,
        auto_recover: bool = True
    ) -> DegradationLevel:
        """
        Mark a component as failed.
        
        Returns:
            New degradation level
        """
        if component not in self.components:
            self.components[component] = ComponentStatus(name=component)
        
        comp = self.components[component]
        comp.failures += 1
        comp.last_failure = error or "unknown"
        comp.healthy = False
        
        # Calculate new degradation level
        self._recalculate_level()
        
        # Save state
        self._save_state()
        
        return self.state.level
    
    def mark_component_recovered(self, component: str) -> DegradationLevel:
        """
        Mark a component as recovered.
        
        Returns:
            New degradation level
        """
        if component in self.components:
            comp = self.components[component]
            comp.healthy = True
            comp.failures = 0
            comp.last_failure = None
        
        # Recalculate level
        self._recalculate_level()
        
        # Exit maintenance mode if all critical components healthy
        if self.state.level == DegradationLevel.NOMINAL:
            self.state.maintenance_mode = False
            self.state.message = "All systems operational"
        
        self._save_state()
        
        return self.state.level
    
    def _recalculate_level(self) -> None:
        """Recalculate degradation level based on component failures."""
        failed = [
            name for name, comp in self.components.items()
            if not comp.healthy and comp.degradation_allowed
        ]
        
        if not failed:
            self.state.level = DegradationLevel.NOMINAL
            self.state.active_components = set(COMPONENT_PRIORITIES.keys())
            self.state.failed_components = set()
            return
        
        # Find the LOWEST priority number (most critical) among failed
        # Priority 1 = most critical (gateway)
        # Priority 10 = least critical (non-essential)
        max_failed_priority = max(
            COMPONENT_PRIORITIES.get(name, 10) for name in failed
        ) if failed else 10
        
        # Determine degradation level based on most critical failed component
        # If most critical failed = priority 1-2 -> EMERGENCY (core down)
        # If most critical failed = priority 3-4 -> SEVERE
        # If most critical failed = priority 5-6 -> MODERATE
        # If most critical failed = priority 7-8 -> LIGHT
        # If most critical failed = priority 9-10 -> NOMINAL (only non-essential down)
        if max_failed_priority <= 2:
            new_level = DegradationLevel.EMERGENCY
        elif max_failed_priority <= 4:
            new_level = DegradationLevel.SEVERE
        elif max_failed_priority <= 6:
            new_level = DegradationLevel.MODERATE
        elif max_failed_priority <= 8:
            new_level = DegradationLevel.LIGHT
        else:
            new_level = DegradationLevel.NOMINAL
        
        self.state.level = new_level
        self.state.failed_components = set(failed)
        self.state.degraded_at = datetime.now().isoformat()
        self.state.last_update = datetime.now().isoformat()
        
        # Calculate active components (those with priority >= max_failed_priority)
        active = [
            name for name, priority in COMPONENT_PRIORITIES.items()
            if priority > max_failed_priority
        ]
        self.state.active_components = set(active)
        
        # Update message
        self.state.message = self._generate_message(failed, new_level)
    
    def _generate_message(self, failed: List[str], level: DegradationLevel) -> str:
        """Generate human-readable status message."""
        if level == DegradationLevel.NOMINAL:
            return "All systems operational"
        
        failed_names = ", ".join(failed)
        
        messages = {
            DegradationLevel.LIGHT: f"Light degradation: {failed_names} temporarily unavailable",
            DegradationLevel.MODERATE: f"Moderate degradation: Some features disabled ({failed_names})",
            DegradationLevel.SEVERE: f"Severe degradation: Only core functionality available ({failed_names})",
            DegradationLevel.EMERGENCY: f"EMERGENCY mode: Minimal functionality ({failed_names})",
            DegradationLevel.DOWN: f"SYSTEM DOWN: {failed_names}",
        }
        
        return messages.get(level, f"Degraded: {failed_names}")
    
    def get_degradation_status(self) -> Dict:
        """
        Get current degradation status.
        
        Returns:
            Dictionary with detailed status
        """
        return {
            "level": self.state.level.value,
            "message": self.state.message,
            "maintenance_mode": self.state.maintenance_mode,
            "active_components": list(self.state.active_components),
            "failed_components": list(self.state.failed_components),
            "degraded_at": self.state.degraded_at,
            "components": {
                name: {
                    "healthy": comp.healthy,
                    "failures": comp.failures,
                    "last_failure": comp.last_failure,
                }
                for name, comp in self.components.items()
            }
        }
    
    def is_feature_available(self, feature: str) -> bool:
        """Check if a feature is available at current degradation level."""
        return feature in self.state.active_components
    
    def enter_maintenance_mode(self, message: str = "Maintenance in progress") -> None:
        """Manually enter maintenance mode."""
        self.state.maintenance_mode = True
        self.state.message = message
        self._save_state()
    
    def exit_maintenance_mode(self) -> None:
        """Exit maintenance mode and return to nominal."""
        self.state.maintenance_mode = False
        self._recalculate_level()
        self._save_state()
    
    def get_available_features(self) -> List[str]:
        """Get list of features available at current degradation level."""
        return list(self.state.active_components)
    
    def get_failed_components(self) -> List[str]:
        """Get list of failed components."""
        return list(self.state.failed_components)
    
    def reset_all(self) -> None:
        """Reset all components to healthy."""
        for comp in self.components.values():
            comp.healthy = True
            comp.failures = 0
            comp.last_failure = None
        
        self.state = DegradationState()
        self._save_state()
    
    def _load_state(self) -> None:
        """Load state from file."""
        if not self.state_file:
            return
        
        try:
            with open(self.state_file) as f:
                data = json.load(f)
            
            self.state = DegradationState(
                level=DegradationLevel(data.get("level", "nominal")),
                active_components=set(data.get("active_components", [])),
                failed_components=set(data.get("failed_components", [])),
                degraded_at=data.get("degraded_at"),
                last_update=data.get("last_update"),
                maintenance_mode=data.get("maintenance_mode", False),
                message=data.get("message", "All systems operational"),
            )
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    
    def _save_state(self) -> None:
        """Save state to file."""
        if not self.state_file:
            return
        
        import os
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        
        with open(self.state_file, "w") as f:
            json.dump({
                "level": self.state.level.value,
                "active_components": list(self.state.active_components),
                "failed_components": list(self.state.failed_components),
                "degraded_at": self.state.degraded_at,
                "last_update": datetime.now().isoformat(),
                "maintenance_mode": self.state.maintenance_mode,
                "message": self.state.message,
            }, f, indent=2)


# Global instance for easy access
STATE_FILE = "/home/clawbot/.openclaw/workspace/data/degradation_state.json"
degradation_manager = GracefulDegradation(STATE_FILE)


# ============ CLI Interface ============

if __name__ == "__main__":
    print("Graceful Degradation - Cascade Failure Handler")
    print("=" * 50)
    print()
    print("Usage:")
    print("  from graceful_degradation import degradation_manager")
    print("  degradation_manager.mark_component_failure('analytics')")
    print()
    print("Degradation Levels:")
    for level in DegradationLevel:
        features = DEGRADATION_FEATURES.get(level, [])
        print("  %s: %s" % (level.value, ", ".join(features)))
    print()
    
    # Demo
    print("Demo:")
    gd = GracefulDegradation()
    
    print("Initial state: %s" % gd.state.level.value)
    
    # Fail non-essential component
    level = gd.mark_component_failure("analytics", "High load")
    print("After analytics fails: %s" % level.value)
    print("  Available: %s" % gd.get_available_features())
    
    # Fail more important component
    level = gd.mark_component_failure("skills", "Timeout")
    print("After skills fails: %s" % level.value)
    print("  Failed: %s" % gd.get_failed_components())
    
    # Recover
    level = gd.mark_component_recovered("skills")
    print("After skills recovers: %s" % level.value)
