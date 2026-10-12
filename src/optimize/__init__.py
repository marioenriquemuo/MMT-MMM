"""Budget optimization helpers (STORY-301).

Step 1: offline response-curve providers.
Step 2–3: SLSQP maximize-KPI / target-KPI allocator + plan-shaped JSON.
"""

from src.optimize.allocator import optimize_budget
from src.optimize.curves import CurveProvider, MetricsJsonCurveProvider, load_curve_means

__all__ = [
    "CurveProvider",
    "MetricsJsonCurveProvider",
    "load_curve_means",
    "optimize_budget",
]
