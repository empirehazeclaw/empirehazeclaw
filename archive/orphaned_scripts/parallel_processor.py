#!/usr/bin/env python3
"""Parallel Task Processor"""
from concurrent.futures import ThreadPoolExecutor

def run_tasks_parallel(tasks, max_workers=8):
    """8 parallel Tasks gleichzeitig"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return executor.map(lambda t: t(), tasks)
