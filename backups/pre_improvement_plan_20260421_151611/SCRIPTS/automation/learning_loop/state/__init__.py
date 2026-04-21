"""State management for Learning Loop."""

STATE_FILE = None  # Set at import time by parent

def load_state():
    """Load loop state with defaults."""
    global STATE_FILE
    from pathlib import Path
    import json
    
    WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
    LOOP_STATE = WORKSPACE / "data" / "ralph_learning_state.json"
    STATE_FILE = LOOP_STATE
    
    defaults = {
        "iteration": 0,
        "loop_score": 0.0,
        "lr": 0.1,
        "pattern_source": "task",
        "stagnation_count": 0,
        "novelty_score": 0.0,
        "last_improvement": None,
        "improvements": [],
        "validated_patterns": [],
        "hypothesis_count": 0,
    }
    
    if not LOOP_STATE.exists():
        return defaults
    
    try:
        with open(LOOP_STATE) as f:
            data = json.load(f)
        return {**defaults, **data}
    except json.JSONDecodeError as e:
        import logging
        logging.getLogger('learning_loop_v3').warning(f"JSON decode error: {e}")
        return defaults
    except FileNotFoundError:
        return defaults
    except Exception as e:
        import logging
        logging.getLogger('learning_loop_v3').error(f"Load error: {e}")
        return defaults

def save_state(state):
    """Save loop state."""
    global STATE_FILE
    from pathlib import Path
    import json
    
    if STATE_FILE is None:
        WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
        STATE_FILE = WORKSPACE / "data" / "ralph_learning_state.json"
    
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
