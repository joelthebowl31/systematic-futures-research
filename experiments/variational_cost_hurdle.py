"""Cost sensitivity from the Variational research appendix; no external data."""
from math import isfinite

def cost_hurdle(costs, rewards, spread_cut):
    """Unit-cost reduction needed to preserve OLP dollar profit."""
    if not all(isfinite(x) for x in (costs, rewards, spread_cut)):
        raise ValueError("Inputs must be finite.")
    if costs <= 0 or rewards < 0 or not 0 <= spread_cut < 1:
        raise ValueError("Invalid costs, rewards, or spread cut.")
    volume_factor = 1 / (1 - spread_cut)
    allowed_costs = costs - rewards * (volume_factor - 1)
    return {
        "required_volume_growth": volume_factor - 1,
        "required_unit_cost_reduction": 1 - allowed_costs / (costs * volume_factor),
        "feasible_at_nonnegative_cost": allowed_costs >= 0,
    }

if __name__ == "__main__":
    print("Synthetic illustration, not observed Variational data:")
    print(cost_hurdle(costs=100, rewards=20, spread_cut=0.20))

