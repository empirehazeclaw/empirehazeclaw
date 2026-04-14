---
name: test-generator
description: Generates unit tests, integration tests, and mock data automatically from source code. Supports Python pytest, Node.js jest, and Bash scripts. Use when you need to add test coverage to existing code or create regression tests.
tags: [testing, pytest, jest, coverage, quality, unit-test]
---

# 🧪 Test Generator Skill

Auto-generate tests from code using MiniMax M2.7.

## When to Use
- After writing new functions/classes
- Before refactoring legacy code
- For code coverage improvement
- Setting up regression testing
- API endpoint testing
- Integration testing setup

## Supported Frameworks

| Language | Framework | Run Command | Coverage |
|----------|-----------|-------------|----------|
| Python | pytest | `pytest` | `--cov` |
| Node.js | jest | `npm test` | `--coverage` |
| Bash | bats | `bats file.bats` | N/A |
| TypeScript | jest | `npx jest` | `--coverage` |

## Test Generation Process

### 1. Analyze Source Code
Identify from the source file:
- Function signatures and return types
- Input parameters and types
- Dependencies and side effects
- Edge cases and boundary conditions
- Error conditions

### 2. Generate Test Template

#### Python (pytest)
```python
import pytest
from module import function

class TestFunction:
    def test_basic_happy_path(self):
        """Test with typical valid input"""
        result = function("valid_input")
        assert result == expected_value
    
    def test_edge_case_empty(self):
        """Test with empty/null input"""
        with pytest.raises(ValueError):
            function("")
    
    def test_edge_case_none(self):
        """Test with None input"""
        result = function(None)
        assert result is None
    
    def test_error_case_invalid(self):
        """Test with invalid input"""
        with pytest.raises(TypeError):
            function(12345)
```

#### Node.js (jest)
```javascript
const { functionName } = require('./module');

describe('functionName', () => {
  test('basic happy path', () => {
    const result = functionName('valid_input');
    expect(result).toBe(expectedValue);
  });
  
  test('handles empty input', () => {
    expect(() => functionName('')).toThrow();
  });
  
  test('handles null input', () => {
    expect(functionName(null)).toBeNull();
  });
});
```

### 3. Mock Data Generation

```python
# Fixtures for pytest
@pytest.fixture
def sample_user():
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "role": "admin"
    }

@pytest.fixture
def sample_config():
    return {
        "debug": True,
        "timeout": 30,
        "max_retries": 3
    }
```

```javascript
// Mock data for jest
const mockUser = {
  id: 1,
  name: 'Test User',
  email: 'test@example.com',
  role: 'admin'
};

const mockConfig = {
  debug: true,
  timeout: 30,
  maxRetries: 3
};
```

## Coverage Reporting

```bash
# Python pytest coverage
pytest --cov=src --cov-report=html --cov-report=term

# Node.js jest coverage
npm test -- --coverage --coverageReporters=html --coverageReporters=text

# Combined report
pytest && echo "Coverage OK" || echo "Coverage failed"
```

## Quality Gates

| Metric | Minimum | Target |
|--------|---------|--------|
| Line coverage | 70% | 90% |
| Function coverage | 80% | 95% |
| Branch coverage | 60% | 80% |

## Example Workflow

```bash
# 1. Analyze Python file
node -e "const tg = require('./skills/test-generator'); console.log(tg.generatePytest('src/utils.py'));"

# 2. Create test file
cat > tests/test_utils.py << 'EOF'
# Generated test content
EOF

# 3. Run tests
pytest tests/test_utils.py -v

# 4. Check coverage
pytest --cov=src tests/
```

## Test Types

| Type | Purpose | When to Use |
|------|---------|-------------|
| Unit | Test single function | Always |
| Integration | Test multiple modules | When features combine |
| Regression | Prevent known bugs | Before releases |
| Smoke | Quick sanity check | After deployments |
| Fuzz | Random inputs | Security critical code |

## Integration
This skill uses Node.js `child_process` to execute test commands.
`list()` returns found test files in the project.
`run()` executes the project's test suite.
