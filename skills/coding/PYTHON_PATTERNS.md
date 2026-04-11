# Python Best Practices & Performance

## 🏃 Performance Patterns

### 1. Lazy Evaluation
```python
# BAD - berechnet alles obwohl nur erstes gebraucht
def get_first_item(items):
    return [f(item) for item in items][0]

# GOOD - Lazy evaluation mit Generator
def get_first_item(items):
    for item in items:
        yield f(item)
    return next(gen)
```

### 2. Caching mit functools
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(x, y):
    # Teure Berechnung
    return x ** y

# Cache leeren wenn nötig
expensive_computation.cache_clear()
```

### 3. Batch Processing
```python
# BAD - Datenbankabfragen in Schleife
for user_id in user_ids:
    user = db.query(user_id)  # N queries

# GOOD - Batch Query
users = db.query("SELECT * FROM users WHERE id IN (?)", user_ids)  # 1 query
```

## 🔒 Security Patterns

### 1. Input Validation
```python
import re

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_path(path: str, allowed_dir: str) -> bool:
    import os.path
    real_path = os.path.realpath(path)
    real_allowed = os.path.realpath(allowed_dir)
    return real_path.startswith(real_allowed)
```

### 2. Secrets aus Env
```python
import os

def get_secret(key: str, required: bool = True) -> str:
    value = os.environ.get(key)
    if not value and required:
        raise ValueError(f"Required env var {key} not set")
    return value
```

## 🧪 Testing Patterns

### 1. Mocking External APIs
```python
from unittest.mock import Mock, patch

def test_with_external_api():
    with patch('requests.get') as mock_get:
        mock_get.return_value = Mock(json=lambda: {'status': 'ok'})
        result = call_external_api()
        assert result['status'] == 'ok'
```

### 2. Fixtures für Tests
```python
import pytest

@pytest.fixture
def sample_data():
    return {
        'name': 'Test',
        'value': 42
    }

def test_with_fixture(sample_data):
    assert sample_data['value'] == 42
```

## 📊 Logging Patterns

### 1. Strukturiertes Logging
```python
import logging

logger = logging.getLogger(__name__)

# BAD
logger.info(f"User {user_id} logged in")

# GOOD - Strukturiert
logger.info("User logged in", extra={
    'user_id': user_id,
    'action': 'login',
    'ip': ip_address
})
```

### 2. Context Manager für Timing
```python
import time
from contextlib import contextmanager

@contextmanager
def timer(name: str):
    start = time.time()
    yield
    elapsed = time.time() - start
    logger.info(f"{name} took {elapsed:.2f}s")

with timer("Data Processing"):
    process_data()
```

## 🔄 Retry Patterns

### 1. Exponential Backoff
```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay * (backoff ** attempt))
        return wrapper
    return decorator

@retry(max_attempts=3, delay=1, backoff=2)
def unreliable_call():
    # Code der manchmal fehlschlägt
    pass
```

## ⚡ Async Patterns

### 1. Async HTTP Calls
```python
import asyncio
import aiohttp

async def fetch_all(urls: list) -> list:
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [await r.json() for r in responses]
```

### 2. Semaphore für Rate Limiting
```python
import asyncio

async def limited_calls(urls: list, max_concurrent: int = 5):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_with_limit(url):
        async with semaphore:
            return await fetch(url)
    
    return await asyncio.gather(*[fetch_with_limit(url) for url in urls])
```

---

*Dokumentiert: 2026-04-11*
*Quelle: Sir HazeClaw Coding Skill Erweiterung*
