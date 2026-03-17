"""
Math Tools — SymPy-powered symbolic mathematics.

Provides equation solving, symbolic differentiation, and expression simplification
for use by the Tutor and Evaluator agents during reasoning.
"""

from typing import Dict, Any, List


def _safe_import_sympy():
    """Lazy import sympy to avoid startup failures if not installed."""
    try:
        import sympy
        return sympy
    except ImportError:
        return None


def solve_equation(equation_str: str, variable: str = "x") -> Dict[str, Any]:
    """
    Solve an equation using SymPy.
    
    Args:
        equation_str: Equation string, e.g. "x**2 - 4 = 0" or "2*x + 3 = 7"
        variable: Variable to solve for (default: "x")
    
    Returns:
        Dict with 'solutions', 'steps', and 'success' keys.
    """
    sympy = _safe_import_sympy()
    if sympy is None:
        return {
            "success": False,
            "error": "SymPy is not installed. Install with: pip install sympy",
            "solutions": [],
            "steps": [],
        }

    try:
        sym_var = sympy.Symbol(variable)
        
        # Parse equation: handle both "expr = val" and bare expressions
        if "=" in equation_str:
            parts = equation_str.split("=", 1)
            lhs = sympy.sympify(parts[0].strip())
            rhs = sympy.sympify(parts[1].strip())
            equation = sympy.Eq(lhs, rhs)
        else:
            equation = sympy.sympify(equation_str)
        
        # Solve
        if isinstance(equation, sympy.Eq):
            solutions = sympy.solve(equation, sym_var)
        else:
            solutions = sympy.solve(equation, sym_var)
        
        # Build step-by-step explanation
        steps = [
            f"Given equation: {equation_str}",
            f"Variable to solve for: {variable}",
            f"Rearranging and solving...",
        ]
        
        solution_strs = [str(s) for s in solutions]
        
        if len(solutions) == 0:
            steps.append("No solutions found.")
        elif len(solutions) == 1:
            steps.append(f"Solution: {variable} = {solutions[0]}")
        else:
            steps.append(f"Solutions: {variable} = {', '.join(solution_strs)}")
        
        return {
            "success": True,
            "solutions": solution_strs,
            "steps": steps,
            "latex": str(sympy.latex(equation)) if isinstance(equation, (sympy.Eq, sympy.Basic)) else "",
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Could not solve equation: {str(e)}",
            "solutions": [],
            "steps": [f"Error parsing '{equation_str}': {str(e)}"],
        }


def differentiate(expression_str: str, variable: str = "x", order: int = 1) -> Dict[str, Any]:
    """
    Compute symbolic derivative of an expression.
    
    Args:
        expression_str: Mathematical expression, e.g. "x**3 + 2*x"
        variable: Variable to differentiate with respect to
        order: Order of differentiation (1 = first derivative, 2 = second, etc.)
    
    Returns:
        Dict with 'result', 'steps', and 'success' keys.
    """
    sympy = _safe_import_sympy()
    if sympy is None:
        return {
            "success": False,
            "error": "SymPy is not installed.",
            "result": "",
            "steps": [],
        }

    try:
        sym_var = sympy.Symbol(variable)
        expr = sympy.sympify(expression_str)
        
        steps = [f"Given: f({variable}) = {expression_str}"]
        
        result = expr
        for i in range(order):
            result = sympy.diff(result, sym_var)
            ordinal = ["first", "second", "third", "fourth", "fifth"][min(i, 4)]
            steps.append(f"The {ordinal} derivative: f{'′' * (i + 1)}({variable}) = {result}")
        
        simplified = sympy.simplify(result)
        if simplified != result:
            steps.append(f"Simplified: {simplified}")
        
        return {
            "success": True,
            "result": str(simplified),
            "steps": steps,
            "latex": str(sympy.latex(simplified)),
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Could not differentiate: {str(e)}",
            "result": "",
            "steps": [],
        }


def simplify_expression(expression_str: str) -> Dict[str, Any]:
    """
    Simplify a mathematical expression using SymPy.
    
    Args:
        expression_str: Expression to simplify, e.g. "(x+1)**2 - x**2"
    
    Returns:
        Dict with 'result', 'steps', and 'success' keys.
    """
    sympy = _safe_import_sympy()
    if sympy is None:
        return {
            "success": False,
            "error": "SymPy is not installed.",
            "result": "",
            "steps": [],
        }

    try:
        expr = sympy.sympify(expression_str)
        
        # Try multiple simplification strategies
        expanded = sympy.expand(expr)
        simplified = sympy.simplify(expr)
        factored = sympy.factor(expr)
        
        steps = [f"Original expression: {expression_str}"]
        
        if expanded != expr:
            steps.append(f"Expanded form: {expanded}")
        if simplified != expr:
            steps.append(f"Simplified form: {simplified}")
        if factored != expr and factored != simplified:
            steps.append(f"Factored form: {factored}")
        
        # Choose the simplest form
        best = min([simplified, expanded, factored], key=lambda x: len(str(x)))
        steps.append(f"Result: {best}")
        
        return {
            "success": True,
            "result": str(best),
            "steps": steps,
            "latex": str(sympy.latex(best)),
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Could not simplify: {str(e)}",
            "result": "",
            "steps": [],
        }


def integrate_expression(expression_str: str, variable: str = "x") -> Dict[str, Any]:
    """
    Compute symbolic integral of an expression.
    """
    sympy = _safe_import_sympy()
    if sympy is None:
        return {"success": False, "error": "SymPy not installed.", "result": "", "steps": []}

    try:
        sym_var = sympy.Symbol(variable)
        expr = sympy.sympify(expression_str)
        result = sympy.integrate(expr, sym_var)
        
        steps = [
            f"Given: ∫ {expression_str} d{variable}",
            f"Result: {result} + C",
        ]
        
        return {
            "success": True,
            "result": f"{result} + C",
            "steps": steps,
            "latex": str(sympy.latex(result)),
        }
    except Exception as e:
        return {"success": False, "error": str(e), "result": "", "steps": []}
