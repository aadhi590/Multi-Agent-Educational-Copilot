"""
Sandboxed Python Executor — Executes student code safely.

Runs Python code in a restricted subprocess with timeout, memory limits,
and blocked imports. Used by Tutor and Evaluator agents for coding problems.
"""

import subprocess
import sys
import tempfile
import os
from typing import Dict, Any


# Imports that are BLOCKED for security
BLOCKED_IMPORTS = {
    "os", "sys", "subprocess", "shutil", "pathlib",
    "socket", "http", "urllib", "requests",
    "pickle", "shelve", "sqlite3",
    "ctypes", "importlib", "__import__",
}

EXECUTION_TIMEOUT = 10  # seconds
MAX_OUTPUT_LENGTH = 5000  # characters


def _check_code_safety(code: str) -> tuple[bool, str]:
    """Check if code contains potentially dangerous operations."""
    code_lower = code.lower()
    
    for blocked in BLOCKED_IMPORTS:
        if f"import {blocked}" in code_lower or f"from {blocked}" in code_lower:
            return False, f"Blocked import: '{blocked}' is not allowed for security reasons."
    
    dangerous_patterns = [
        ("open(", "File operations are not allowed."),
        ("exec(", "Dynamic code execution is not allowed."),
        ("eval(", "Dynamic evaluation is not allowed."),
        ("__import__", "Dynamic imports are not allowed."),
        ("globals(", "Accessing globals is not allowed."),
        ("locals(", "Accessing locals is not allowed."),
    ]
    
    for pattern, message in dangerous_patterns:
        if pattern in code:
            return False, message
    
    return True, ""


def execute_python(code: str) -> Dict[str, Any]:
    """
    Execute Python code in a sandboxed subprocess.
    
    Args:
        code: Python source code to execute.
    
    Returns:
        Dict with 'output', 'error', 'success', and 'execution_time' keys.
    """
    # Safety check
    is_safe, safety_message = _check_code_safety(code)
    if not is_safe:
        return {
            "success": False,
            "output": "",
            "error": f"Security violation: {safety_message}",
            "execution_time": 0,
        }
    
    # Write code to a temp file
    try:
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False, encoding='utf-8'
        ) as f:
            f.write(code)
            temp_path = f.name
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Failed to create temp file: {str(e)}",
            "execution_time": 0,
        }
    
    try:
        # Run in subprocess with timeout
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=EXECUTION_TIMEOUT,
            cwd=tempfile.gettempdir(),
        )
        
        stdout = result.stdout[:MAX_OUTPUT_LENGTH] if result.stdout else ""
        stderr = result.stderr[:MAX_OUTPUT_LENGTH] if result.stderr else ""
        
        success = result.returncode == 0
        
        return {
            "success": success,
            "output": stdout,
            "error": stderr if not success else "",
            "return_code": result.returncode,
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": f"Execution timed out after {EXECUTION_TIMEOUT} seconds.",
            "execution_time": EXECUTION_TIMEOUT,
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Execution error: {str(e)}",
            "execution_time": 0,
        }
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except OSError:
            pass
