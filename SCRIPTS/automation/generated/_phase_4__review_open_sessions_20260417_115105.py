#!/usr/bin/env python3
"""
PHASE 4: Session Management and Optimization
Reviews open sessions, closes orphaned sessions, measures average session length,
and identifies optimizations.
"""

import json
import time
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List
import uuid
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Session:
    """Represents a user session with metadata."""
    session_id: str
    user_id: str
    start_time: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True
    request_count: int = 0
    metadata: Dict = field(default_factory=dict)
    
    def get_duration_seconds(self) -> float:
        """Calculate session duration in seconds."""
        return (datetime.now() - self.start_time).total_seconds()
    
    def get_idle_seconds(self) -> float:
        """Calculate idle time since last activity."""
        return (datetime.now() - self.last_activity).total_seconds()
    
    def to_dict(self) -> dict:
        """Convert session to dictionary."""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        data['last_activity'] = self.last_activity.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Session':
        """Create session from dictionary."""
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        return cls(**data)


class SessionStore:
    """Manages session storage and operations."""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.max_idle_seconds = 1800  # 30 minutes
        self.max_session_seconds = 86400  # 24 hours
    
    def add_session(self, session: Session) -> bool:
        """Add a new session."""
        try:
            self.sessions[session.session_id] = session
            logger.info(f"Session {session.session_id} added for user {session.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve a session by ID."""
        try:
            return self.sessions.get(session_id)
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    def remove_session(self, session_id: str) -> bool:
        """Remove a session."""
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"Session {session_id} removed")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove session {session_id}: {e}")
            return False
    
    def get_active_sessions(self) -> List[Session]:
        """Get all active sessions."""
        return [s for s in self.sessions.values() if s.is_active]
    
    def get_orphaned_sessions(self, threshold_seconds: float = None) -> List[Session]:
        """Identify sessions with no recent activity (orphaned)."""
        if threshold_seconds is None:
            threshold_seconds = self.max_idle_seconds
        
        orphaned = []
        for session in self.sessions.values():
            if session.get_idle_seconds() > threshold_seconds:
                orphaned.append(session)
        
        return orphaned
    
    def cleanup_orphaned(self) -> Dict[str, any]:
        """Close all orphaned sessions and return statistics."""
        try:
            orphaned = self.get_orphaned_sessions()
            cleaned_ids = []
            
            for session in orphaned:
                session.is_active = False
                cleaned_ids.append(session.session_id)
                self.remove_session(session.session_id)
            
            return {
                'orphaned_count': len(cleaned_ids),
                'session_ids': cleaned_ids,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to cleanup orphaned sessions: {e}")
            return {'error': str(e)}
    
    def calculate_average_session_length(self) -> float:
        """Calculate average session length in seconds."""
        try:
            active_sessions = self.get_active_sessions()
            if not active_sessions:
                return 0.0
            
            total_duration = sum(s.get_duration_seconds() for s in active_sessions)
            return total_duration / len(active_sessions)
        except Exception as e:
            logger.error(f"Failed to calculate average session length: {e}")
            return 0.0
    
    def get_session_statistics(self) -> Dict:
        """Get comprehensive session statistics."""
        try:
            sessions = list(self.sessions.values())
            if not sessions:
                return {'error': 'No sessions available'}
            
            durations = [s.get_duration_seconds() for s in sessions]
            idle_times = [s.get_idle_seconds() for s in sessions]
            request_counts = [s.request_count for s in sessions]
            
            return {
                'total_sessions': len(sessions),
                'active_sessions': len(self.get_active_sessions()),
                'orphaned_sessions': len(self.get_orphaned_sessions()),
                'avg_duration_seconds': sum(durations) / len(durations),
                'max_duration_seconds': max(durations),
                'min_duration_seconds': min(durations),
                'avg_idle_seconds': sum(idle_times) / len(idle_times),
                'avg_request_count': sum(request_counts) / len(request_counts),
                'total_requests': sum(request_counts)
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {'error': str(e)}


class SessionOptimizer:
    """Identifies and suggests optimizations for session management."""
    
    def __init__(self, session_store: SessionStore):
        self.session_store = session_store
        self.optimization_threshold = 0.75  # 75% threshold
    
    def identify_optimization(self) -> Dict:
        """Identify the most impactful optimization opportunity."""
        try:
            stats = self.session_store.get_session_statistics()
            
            if 'error' in stats:
                return {'optimization': 'No data available', 'impact': 'N/A'}
            
            # Analyze multiple factors
            orphaned_ratio = stats['orphaned_sessions'] / max(stats['total_sessions'], 1)
            avg_idle = stats['avg_idle_seconds']
            avg_duration = stats['avg_duration_seconds']
            
            optimizations = []
            
            # High orphaned ratio optimization
            if orphaned_ratio > self.optimization_threshold:
                optimizations.append({
                    'type': 'Reduce Idle Timeout',
                    'description': f'High orphaned ratio ({orphaned_ratio:.1%}). '
                                   f'Consider reducing idle timeout from 1800s to 900s.',
                    'impact': 'high',
                    'potential_savings': f'{stats["orphaned_sessions"]} sessions could be cleaned earlier'
                })
            
            # Long idle times optimization
            if avg_idle > 600:
                optimizations.append({
                    'type': 'Implement Session Ping',
                    'description': f'High average idle time ({avg_idle:.0f}s). '
                                   f'Implement periodic ping to detect disconnected clients.',
                    'impact': 'medium',
                    'potential_savings': 'Reduce server memory usage by detecting stale connections'
                })
            
            # Long average session optimization
            if avg_duration > 7200:
                optimizations.append({
                    'type': 'Add Session Refresh',
                    'description': f'Long average session ({avg_duration/3600:.1f}h). '
                                   f'Add session refresh mechanism to validate active sessions.',
                    'impact': 'medium',
                    'potential_savings': 'Ensure session data remains current'
                })
            
            # Low request count optimization
            if stats['avg_request_count'] < 5 and stats['active_sessions'] > 10:
                optimizations.append({
                    'type': 'Batch Session Updates',
                    'description': 'Low request count per session. Consider batching updates.',
                    'impact': 'low',
                    'potential_savings': 'Reduce database writes'
                })
            
            # Return best optimization
            if optimizations:
                best = max(optimizations, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['impact']])
                return {
                    'primary_optimization': best,
                    'all_optimizations': optimizations,
                    'stats_used': stats
                }
            
            return {
                'primary_optimization': {
                    'type': 'No Critical Issues',
                    'description': 'Session management is operating within normal parameters.',
                    'impact': 'none'
                },
                'all_optimizations': [],
                'stats_used': stats
            }
            
        except Exception as e:
            logger.error(f"Failed to identify optimization: {e}")
            return {'error': str(e)}


class SessionManager:
    """Main session management interface."""
    
    def __init__(self):
        self.store = SessionStore()
        self.optimizer = SessionOptimizer(self.store)
        self._generate_sample_sessions()
    
    def _generate_sample_sessions(self):
        """Generate sample sessions for demonstration."""
        try:
            user_ids = [f"user_{i}" for i in range(1, 11)]
            ips = ["192.168.1.100", "10.0.0.50", "172.16.0.25", "192.168.2.50"]
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64) Firefox/121.0"
            ]
            
            base_time = datetime.now()
            
            for i, user_id in enumerate(user_ids):
                # Create sessions with varying characteristics
                is_recent = i < 6
                start_offset = random.randint(100, 5000) if is_recent else random.randint(10000, 80000)
                
                session = Session(
                    session_id=str(uuid.uuid4()),
                    user_id=user_id,
                    start_time=base_time - timedelta(seconds=start_offset),
                    last_activity=base_time - timedelta(seconds=random.randint(0, start_offset)),
                    ip_address=random.choice(ips),
                    user_agent=random.choice(user_agents),
                    is_active=random.choice([True, True, True, False]),
                    request_count=random.randint(1, 50),
                    metadata={'source': 'demo', 'index': i}
                )
                
                self.store.add_session(session)
            
            logger.info(f"Generated {len(user_ids)} sample sessions")
            
        except Exception as e:
            logger.error(f"Failed to generate sample sessions: {e}")
    
    def run_phase4(self) -> Dict:
        """Execute Phase 4: Review and optimize sessions."""
        try:
            logger.info("=" * 60)
            logger.info("PHASE 4: Session Review and Optimization")
            logger.info("=" * 60)
            
            # Step 1: Review open sessions
            logger.info("\n[STEP 1] Reviewing Open Sessions...")
            active_sessions = self.store.get_active_sessions()
            logger.info(f"Found {len(active_sessions)} active sessions")
            
            for session in active_sessions[:5]:  # Show first 5
                logger.info(
                    f"  - Session: {session.session_id[:8]}... "
                    f"User: {session.user_id} "
                    f"Duration: {session.get_duration_seconds():.0f}s "
                    f"Idle: {session.get_idle_seconds():.0f}s"
                )
            
            # Step 2: Identify orphaned sessions
            logger.info("\n[STEP 2] Identifying Orphaned Sessions...")
            orphaned = self.store.get_orphaned_sessions()
            logger.info(f"Found {len(orphaned)} orphaned sessions")
            
            for session in orphaned:
                logger.warning(
                    f"  - Orphaned: {session.session_id[:8]}... "
                    f"(Idle: {session.get_idle_seconds():.0f}s)"
                )
            
            # Step 3: Close orphaned sessions
            logger.info("\n[STEP 3] Closing Orphaned Sessions...")
            cleanup_result = self.store.cleanup_orphaned()
            logger.info(f"Closed {cleanup_result.get('orphaned_count', 0)} sessions")
            
            # Step 4: Measure average session length
            logger.info("\n[STEP 4] Measuring Average Session Length...")
            avg_length = self.store.calculate_average_session_length()
            logger.info(f"Average session length: {avg_length:.2f} seconds ({avg_length/60:.2f} minutes)")
            
            # Get comprehensive statistics
            stats = self.store.get_session_statistics()
            logger.info(f"Statistics: {json.dumps(stats, indent=4)}")
            
            # Step 5: Identify optimization
            logger.info("\n[STEP 5] Identifying Optimization...")
            optimization_result = self.optimizer.identify_optimization()
            
            if 'primary_optimization' in optimization_result:
                opt = optimization_result['primary_optimization']
                logger.info(f"\n{'='*60}")
                logger.info("IDENTIFIED OPTIMIZATION:")
                logger.info(f"{'='*60}")
                logger.info(f"Type: {opt['type']}")
                logger.info(f"Description: {opt['description']}")
                logger.info(f"Impact: {opt['impact']}")
                if 'potential_savings' in opt:
                    logger.info(f"Potential Savings: {opt['potential_savings']}")
            
            # Return complete results
            return {
                'status': 'completed',
                'timestamp': datetime.now().isoformat(),
                'active_sessions': len(active_sessions),
                'orphaned_closed': cleanup_result.get('orphaned_count', 0),
                'avg_session_length_seconds': avg_length,
                'statistics': stats,
                'optimization': optimization_result
            }
            
        except Exception as e:
            logger.error(f"Phase 4 failed: {e}")
            return {'status': 'error', 'error': str(e)}


class SessionAPISimulator:
    """Simulates API endpoints for session management."""
    
    def __init__(self, session_manager: SessionManager):
        self.manager = session_manager
        self.request_counter = 0
    
    def simulate_request(self, session_id: str) -> bool:
        """Simulate an API request updating session."""
        try:
            session = self.manager.store.get_session(session_id)
            if session:
                session.last_activity = datetime.now()
                session.request_count += 1
                self.request_counter += 1
                return True
            return False
        except Exception as e:
            logger.error(f"Request simulation failed: {e}")
            return False
    
    def simulate_traffic(self, duration_seconds: int = 5):
        """Simulate incoming traffic."""
        logger.info(f"Simulating traffic for {duration_seconds} seconds...")
        
        active_sessions = self.manager.store.get_active_sessions()
        end_time = time.time() + duration_seconds
        
        while time.time() < end_time:
            if active_sessions:
                session = random.choice(active_sessions)
                self.simulate_request(session.session_id)
            time.sleep(0.1)
        
        logger.info(f"Simulated {self.request_counter} requests")


def export_report(session_manager: SessionManager, filepath: str = "session_report.json"):
    """Export session report to JSON file."""
    try:
        result = session_manager.run_phase4()
        
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        logger.info(f"Report exported to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to export report: {e}")
        return False


def print_console_report(session_manager: SessionManager):
    """Print formatted report to console."""
    try:
        result = session_manager.run_phase4()
        
        print("\n" + "=" * 70)
        print("PHASE 4 SESSION MANAGEMENT REPORT")
        print("=" * 70)
        
        print(f"\nExecution Time: {result['timestamp']}")
        print(f"Status: {result['status']}")
        
        print("\n--- Session Overview ---")
        print(f"Active Sessions: {result['active_sessions']}")
        print(f"Orphaned Sessions Closed: {result['orphaned_closed']}")
        print(f"Average Session Length: {result['avg_session_length_seconds']:.2f}s "
              f"({result['avg_session_length_seconds']/60:.2f} min)")
        
        print("\n--- Statistics ---")
        stats = result['statistics']
        print(f"Total Sessions: {stats.get('total_sessions', 'N/A')}")
        print(f"Max Duration: {stats.get('max_duration_seconds', 0)/3600:.2f} hours")
        print(f"Min Duration: {stats.get('min_duration_seconds', 0):.0f} seconds")
        print(f"Avg Idle Time: {stats.get('avg_idle_seconds', 0):.0f} seconds")
        print(f"Total Requests: {stats.get('total_requests', 0)}")
        
        print("\n--- Optimization Identified ---")
        opt = result['optimization'].get('primary_optimization', {})
        print(f"Type: {opt.get('type', 'N/A')}")
        print(f"Description: {opt.get('description', 'N/A')}")
        print(f"Impact: {opt.get('impact', 'N/A')}")
        
        if opt.get('potential_savings'):
            print(f"Potential Savings: {opt['potential_savings']}")
        
        print("\n" + "=" *