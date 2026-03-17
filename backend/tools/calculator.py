"""
Calculator Tool — Safe numeric computation.

Provides a safe evaluate function for mathematical expressions
without exposing Python's eval() directly.
"""

import math
import re
from typing import Dict, Any


# Safe math functions available in calculations
SAFE_MATH_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
    "int": int,
    "float": float,
    # Math module functions
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "atan2": math.atan2,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "exp": math.exp,
    "ceil": math.ceil,
    "floor": math.floor,
    "factorial": math.factorial,
    "gcd": math.gcd,
    "pi": math.pi,
    "e": math.e,
    "inf": math.inf,
}


def calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate a mathematical expression.
    
    Args:
        expression: Math expression string, e.g. "sqrt(144) + 3**2"
    
    Returns:
        Dict with 'result', 'expression', and 'success' keys.
    """
    # Sanitize: block dangerous patterns
    blocked = ["import", "exec", "eval", "__", "open", "os.", "sys."]
    expr_lower = expression.lower()
    for b in blocked:
        if b in expr_lower:
            return {
                "success": False,
                "error": f"Expression contains blocked pattern: '{b}'",
                "result": None,
                "expression": expression,
            }
    
    try:
        # Use restricted globals with only math functions
        restricted_globals = {"__builtins__": {}}
        restricted_globals.update(SAFE_MATH_FUNCTIONS)
        
        result = eval(expression, restricted_globals)
        
        # Format result
        if isinstance(result, float):
            # Avoid floating point noise
            if result == int(result) and abs(result) < 1e15:
                result = int(result)
            else:
                result = round(result, 10)
        
        return {
            "success": True,
            "result": result,
            "expression": expression,
            "formatted": str(result),
        }
        
    except ZeroDivisionError:
        return {
            "success": False,
            "error": "Division by zero",
            "result": None,
            "expression": expression,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Calculation error: {str(e)}",
            "result": None,
            "expression": expression,
        }


def unit_convert(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """Basic unit conversion for common educational units."""
    conversions = {
        ("m", "cm"): 100,
        ("cm", "m"): 0.01,
        ("km", "m"): 1000,
        ("m", "km"): 0.001,
        ("kg", "g"): 1000,
        ("g", "kg"): 0.001,
        ("celsius", "fahrenheit"): lambda v: v * 9 / 5 + 32,
        ("fahrenheit", "celsius"): lambda v: (v - 32) * 5 / 9,
        ("rad", "deg"): lambda v: v * 180 / math.pi,
        ("deg", "rad"): lambda v: v * math.pi / 180,
    }
    
    key = (from_unit.lower(), to_unit.lower())
    if key not in conversions:
        return {"success": False, "error": f"Unknown conversion: {from_unit} → {to_unit}"}
    
    factor = conversions[key]
    if callable(factor):
        result = factor(value)
    else:
        result = value * factor
    
    return {
        "success": True,
        "result": round(result, 6),
        "formatted": f"{value} {from_unit} = {round(result, 6)} {to_unit}",
    }
