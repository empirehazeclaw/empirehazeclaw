const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function run(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf8', maxBuffer: 10*1024*1024 });
  } catch (e) {
    return `Error: ${e.message}`;
  }
}

module.exports = {
  name: 'test-generator',
  
  // List test files in project
  list() {
    return run('find . -name "*.test.js" -o -name "*_test.py" -o -name "test_*.py" 2>/dev/null | head -20');
  },
  
  // Run tests
  run(args = '') {
    return run(`npm test -- ${args} 2>&1 || pytest ${args} 2>&1 || echo "No test framework found"`);
  },
  
  // Coverage report
  coverage() {
    return run('npm run test:coverage 2>/dev/null || pytest --cov 2>/dev/null || echo "No coverage tool"');
  },
  
  // Generate pytest for Python file
  generatePytest(filePath) {
    const base = path.basename(filePath, '.py');
    const testFile = `test_${base}.py`;
    return `Generated: ${testFile}\n# Template:\n# import pytest\n# from ${base} import *\n#\n# def test_${base}_basic():\n#     assert True`;
  },
  
  // Generate jest test for JS file  
  generateJest(filePath) {
    const base = path.basename(filePath, '.js');
    const testFile = `${base}.test.js`;
    return `Generated: ${testFile}\n// Template:\n// describe('${base}', () => {\n//   test('basic', () => {\n//     expect(true).toBe(true);\n//   });\n// });`;
  }
};
