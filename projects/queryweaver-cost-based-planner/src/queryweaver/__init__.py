"""QueryWeaver: deterministic cost-based SQL planning reference implementation."""
from .parser import parse, SQLSyntaxError
from .planner import optimize, naive_plan, explain, to_dot, PlanningError
from .catalog import Catalog, CatalogError, from_rows
from .engine import execute

__all__ = ["parse", "SQLSyntaxError", "optimize", "naive_plan", "explain", "to_dot",
           "PlanningError", "Catalog", "CatalogError", "from_rows", "execute"]
__version__ = "1.0.0"
