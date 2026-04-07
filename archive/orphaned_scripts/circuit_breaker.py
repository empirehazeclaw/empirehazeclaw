#!/usr/bin/env python3
"""
Circuit Breaker - Prevent cascade failures
"""
import time
from enum import Enum

class State(Enum):
    CLOSED = 0
    OPEN = 1
    HALF_OPEN = 2

class CircuitBreaker:
    def __init__(self, threshold=5, timeout=60):
        self.threshold = threshold
        self.timeout = timeout
        self.failures = 0
        self.state = State.CLOSED
        self.last_failure = 0
    
    def call(self, func):
        if self.state == State.OPEN:
            if time.time() - self.last_failure > self.timeout:
                self.state = State.HALF_OPEN
            else:
                raise Exception("Circuit OPEN")
        
        try:
            result = func()
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        self.failures = 0
        self.state = State.CLOSED
    
    def on_failure(self):
        self.failures += 1
        self.last_failure = time.time()
        if self.failures >= self.threshold:
            self.state = State.OPEN
