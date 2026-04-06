#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          CODING AGENT - ENHANCED                            ║
║          Code Gen · Docker Sandbox · Auto-Debugging        ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - Multi-Language Code Generation
  - Docker Sandbox Execution (wenn verfügbar)
  - Auto-Debugging mit Retry-Loop
  - Unit Tests Generation
  - Code Review & Refactoring
  - Syntax Validation

Hinweis: LLM-Routing wird NICHT verwendet
"""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

log = logging.getLogger("openclaw.coding")

# Konfiguration
MAX_DEBUG_ITERATIONS = 3
EXECUTION_TIMEOUT = 15
MAX_OUTPUT_CHARS = 3000


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    BASH = "bash"
    SQL = "sql"
    TYPESCRIPT = "typescript"
    RUST = "rust"
    GO = "go"
    UNKNOWN = "unknown"


@dataclass
class CodeResult:
    """Ergebnis einer Code-Ausführung"""
    success: bool
    output: str
    error: Optional[str]
    language: Language
    execution_time: float
    iterations: int


class CodingAgent:
    """
    Enhanced Coding Agent mit:
    - Docker Sandbox
    - Auto-Debugging (3x Retry)
    - Multi-Language Support
    - Code Review
    """
    
    def __init__(self):
        self.workspace = Path("/home/clawbot/.openclaw/workspace")
        self.docker_available = self.check_docker()
    
    def check_docker(self) -> bool:
        """Prüfe ob Docker verfügbar ist"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def detect_language(self, code: str) -> Language:
        """Erkenne Programmiersprache"""
        code = code.strip().lower()
        
        if "def " in code or "import " in code or "print(" in code:
            return Language.PYTHON
        elif "function " in code or "const " in code or "let " in code or "=>" in code:
            return Language.JAVASCRIPT
        elif "#!/bin/bash" in code or code.startswith("if ") or "echo " in code:
            return Language.BASH
        elif "select " in code.lower() or "insert " in code.lower():
            return Language.SQL
        elif "fn " in code or "let mut" in code:
            return Language.RUST
        elif "func " in code or "package " in code:
            return Language.GO
        
        return Language.UNKNOWN
    
    async def generate_code(self, prompt: str, language: Language = None) -> str:
        """
        Generiere Code basierend auf Prompt
        
        In real implementation, dies würde den LLM aufrufen.
        Hier: Template-basierte Generierung.
        """
        # Simple template generation
        if language == Language.PYTHON:
            return self.generate_python(prompt)
        elif language == Language.JAVASCRIPT:
            return self.generate_javascript(prompt)
        
        return "# Code generation requires LLM integration"
    
    def generate_python(self, prompt: str) -> str:
        """Generate Python code from prompt"""
        if "hello" in prompt.lower():
            return '''#!/usr/bin/env python3
"""Hello World Script"""

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
'''
        elif "api" in prompt.lower():
            return '''#!/usr/bin/env python3
"""Simple API Example"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "Hello API"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
        return "# Implement your logic here"
    
    def generate_javascript(self, prompt: str) -> str:
        """Generate JavaScript code"""
        if "hello" in prompt.lower():
            return '''// Hello World
console.log("Hello, World!");
'''
        return "// Implement your logic here"
    
    async def execute_code(self, code: str, language: Language = None) -> CodeResult:
        """
        Führe Code aus (mit Docker wenn möglich)
        """
        if not language:
            language = self.detect_language(code)
        
        start_time = time.time()
        
        # Try Docker if available
        if self.docker_available:
            return await self.execute_docker(code, language, start_time)
        
        # Fallback: Direct execution
        return await self.execute_direct(code, language, start_time)
    
    async def execute_docker(self, code: str, language: Language, start_time: float) -> CodeResult:
        """Execute in Docker sandbox"""
        
        # Map language to docker image
        images = {
            Language.PYTHON: "python:3.11-slim",
            Language.JAVASCRIPT: "node:18-slim",
            Language.BASH: "bash:latest"
        }
        
        image = images.get(language, "python:3.11-slim")
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix=f".{language.value}", delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Run in docker
            result = subprocess.run([
                "docker", "run", "--rm",
                "-v", f"{temp_file}:/code",
                "-w", "/code",
                image,
                "python" if language == Language.PYTHON else "node",
                "/code"
            ], capture_output=True, text=True, timeout=EXECUTION_TIMEOUT)
            
            execution_time = time.time() - start_time
            
            return CodeResult(
                success=result.returncode == 0,
                output=result.stdout[:MAX_OUTPUT_CHARS],
                error=result.stderr if result.returncode != 0 else None,
                language=language,
                execution_time=execution_time,
                iterations=1
            )
            
        except subprocess.TimeoutExpired:
            return CodeResult(
                success=False,
                output="",
                error="Execution timeout",
                language=language,
                execution_time=EXECUTION_TIMEOUT,
                iterations=1
            )
        except Exception as e:
            return CodeResult(
                success=False,
                output="",
                error=str(e),
                language=language,
                execution_time=time.time() - start_time,
                iterations=1
            )
        finally:
            os.unlink(temp_file)
    
    async def execute_direct(self, code: str, language: Language, start_time: float) -> CodeResult:
        """Execute code directly (less secure)"""
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix=f".{language.value}", delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            cmd = {
                Language.PYTHON: ["python3", temp_file],
                Language.JAVASCRIPT: ["node", temp_file],
                Language.BASH: ["bash", temp_file]
            }.get(language)
            
            if not cmd:
                return CodeResult(
                    success=False,
                    output="",
                    error=f"Unsupported language: {language}",
                    language=language,
                    execution_time=time.time() - start_time,
                    iterations=1
                )
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=EXECUTION_TIMEOUT
            )
            
            execution_time = time.time() - start_time
            
            return CodeResult(
                success=result.returncode == 0,
                output=result.stdout[:MAX_OUTPUT_CHARS],
                error=result.stderr if result.returncode != 0 else None,
                language=language,
                execution_time=execution_time,
                iterations=1
            )
            
        except subprocess.TimeoutExpired:
            return CodeResult(
                success=False,
                output="",
                error="Execution timeout",
                language=language,
                execution_time=EXECUTION_TIMEOUT,
                iterations=1
            )
        except Exception as e:
            return CodeResult(
                success=False,
                output="",
                error=str(e),
                language=language,
                execution_time=time.time() - start_time,
                iterations=1
            )
        finally:
            os.unlink(temp_file)
    
    async def debug_and_fix(self, code: str, error: str) -> str:
        """
        Auto-Debugging: Versuche Code zu fixen basierend auf Error
        
        Returns:
            Fixed code
        """
        log.info(f"🔧 Auto-Debugging: {error[:100]}...")
        
        # Simple fixes based on common errors
        fixes = [
            # Indentation
            (r'IndentationError', lambda c: self.fix_indentation(c)),
            # Syntax errors
            (r'SyntaxError', lambda c: self.fix_syntax(c)),
            # Import errors
            (r'ImportError|ModuleNotFoundError', lambda c: self.fix_imports(c)),
            # Name errors
            (r'NameError', lambda c: self.fix_names(c)),
            # Type errors
            (r'TypeError', lambda c: self.fix_types(c)),
        ]
        
        fixed_code = code
        
        for error_pattern, fix_func in fixes:
            if re.search(error_pattern, error):
                fixed_code = fix_func(fixed_code)
        
        return fixed_code
    
    def fix_indentation(self, code: str) -> str:
        """Fix indentation errors"""
        lines = code.split('\n')
        fixed = []
        for line in lines:
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                # Add proper indentation
                if line.startswith('def ') or line.startswith('class ') or line.startswith('if '):
                    line = '    ' + line
            fixed.append(line)
        return '\n'.join(fixed)
    
    def fix_syntax(self, code: str) -> str:
        """Fix common syntax errors"""
        # Add missing parentheses
        code = re.sub(r'print\s+["\'](.*?)["\']', r'print("\1")', code)
        # Fix missing colons
        code = re.sub(r'(def|class|if|for|while)\s+([^\n]+)\n([^#\s])', r'\1 \2:\n\3', code)
        return code
    
    def fix_imports(self, code: str) -> str:
        """Fix import errors"""
        # Add common imports if missing
        if "import " not in code and "from " not in code:
            return "import sys\n" + code
        return code
    
    def fix_names(self, code: str) -> str:
        """Fix name errors"""
        # Define common undefined names
        undefined = {
            "json": "import json\n",
            "os": "import os\n",
            "sys": "import sys\n",
            "re": "import re\n"
        }
        
        imports = []
        for name, import_stmt in undefined.items():
            if name in code and import_stmt.strip() not in code:
                imports.append(import_stmt)
        
        return ''.join(imports) + code
    
    def fix_types(self, code: str) -> str:
        """Fix type errors"""
        # Simple type conversions
        code = re.sub(r'str\(([^)]+)\)\+', r'str(\1) +', code)
        return code
    
    async def run_with_debug(self, code: str) -> CodeResult:
        """
        Führe Code aus mit Auto-Debugging
        Retry-Loop bis MAX_DEBUG_ITERATIONS
        """
        language = self.detect_language(code)
        
        for iteration in range(1, MAX_DEBUG_ITERATIONS + 1):
            log.info(f"🔄 Attempt {iteration}/{MAX_DEBUG_ITERATIONS}")
            
            result = await self.execute_code(code, language)
            
            if result.success:
                result.iterations = iteration
                return result
            
            if iteration < MAX_DEBUG_ITERATIONS and result.error:
                # Try to fix
                code = await self.debug_and_fix(code, result.error)
                log.info(f"   → Fixed, retrying...")
        
        return result
    
    async def generate_tests(self, code: str, language: Language = None) -> str:
        """Generiere Unit Tests"""
        if not language:
            language = self.detect_language(code)
        
        if language == Language.PYTHON:
            return self.generate_python_tests(code)
        
        return "# Test generation not supported for this language"
    
    def generate_python_tests(self, code: str) -> str:
        """Generate Python unit tests"""
        # Extract function names
        functions = re.findall(r'def\s+(\w+)\s*\(', code)
        
        if not functions:
            return "# No functions found to test"
        
        test_code = '''#!/usr/bin/env python3
"""Unit Tests"""
import unittest

'''
        
        for func in functions:
            test_code += f'''
class Test{func.capitalize()}(unittest.TestCase):
    def test_{func}(self):
        # TODO: Add test assertions
        pass

'''
        test_code += '''
if __name__ == "__main__":
    unittest.main()
'''
        
        return test_code
    
    def review_code(self, code: str) -> Dict:
        """Code Review mit Empfehlungen"""
        issues = []
        
        # Check for common issues
        issues_check = [
            (r'eval\s*\(', "HIGH", "Avoid using eval()"),
            (r'exec\s*\(', "HIGH", "Avoid using exec()"),
            (r'print\s*\(', "LOW", "Consider logging instead of print"),
            (r'except:\s*$', "MEDIUM", "Bare except clause - specify exception type"),
            (r'while\s+True:', "LOW", "Potential infinite loop"),
            (r'global\s+\w+', "MEDIUM", "Avoid global variables"),
        ]
        
        for pattern, severity, message in issues_check:
            if re.search(pattern, code, re.MULTILINE):
                issues.append({"severity": severity, "message": message})
        
        return {
            "issues_found": len(issues),
            "issues": issues,
            "score": max(0, 100 - len(issues) * 15),
            "recommendations": [
                "Add docstrings",
                "Add type hints",
                "Add error handling",
                "Consider using logging"
            ]
        }


async def main():
    """CLI Test"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Coding Agent")
    parser.add_argument("--execute", help="Code to execute")
    parser.add_argument("--review", help="Code to review")
    parser.add_argument("--test", help="Generate tests for this code")
    
    args = parser.parse_args()
    
    agent = CodingAgent()
    
    print(f"🐳 Docker available: {agent.docker_available}")
    
    if args.execute:
        print(f"\n📝 Executing:\n{args.execute}\n")
        result = await agent.run_with_debug(args.execute)
        print(f"✅ Success: {result.success}")
        print(f"   Output: {result.output[:200]}")
        if result.error:
            print(f"   Error: {result.error[:200]}")
        print(f"   Iterations: {result.iterations}")
    
    if args.review:
        print(f"\n🔍 Code Review:")
        review = agent.review_code(args.review)
        print(f"   Score: {review['score']}/100")
        print(f"   Issues: {review['issues_found']}")
        for issue in review['issues']:
            print(f"   - [{issue['severity']}] {issue['message']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
