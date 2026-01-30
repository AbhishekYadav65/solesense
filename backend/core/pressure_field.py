"""
Spatial Pressure Field Module

Generates a bounded 2D pressure distribution over the shoe sole.
No wrap-around. No edge leakage. Deterministic smoothing.
"""

import numpy as np
from core.constants import GRID_ROWS, GRID_COLS


def _base_longitudinal_profile():
    """
    Heel-to-toe base pressure profile.
    """
    x = np.linspace(0, 1, GRID_ROWS)
    return 1.2 - x


def _apply_arch_bias(profile, arch_bias):
    """
    Redistribute pressure in the midfoot region.
    """
    mid_start = int(0.35 * GRID_ROWS)
    mid_end = int(0.65 * GRID_ROWS)

    profile[mid_start:mid_end] += arch_bias
    return profile


def _expand_to_grid(longitudinal_profile):
    """
    Expand 1D profile across foot width.
    """
    return np.tile(
        longitudinal_profile.reshape(-1, 1),
        (1, GRID_COLS)
    )


def _apply_contact_capacity(grid, capacity):
    """
    Shape pressure concentration without geometry distortion.
    """
    exponent = max(0.5, 1.5 - capacity)
    return np.power(grid, exponent)


def _smooth_grid_bounded(grid, stiffness_factor, iterations=3):
    """
    Bounded smoothing with zero-flux edges.
    """
    steps = int((1.0 - stiffness_factor) * iterations)
    rows, cols = grid.shape

    for _ in range(steps):
        new_grid = grid.copy()

        for i in range(rows):
            for j in range(cols):
                neighbors = [grid[i, j]]

                if i > 0:
                    neighbors.append(grid[i - 1, j])
                if i < rows - 1:
                    neighbors.append(grid[i + 1, j])
                if j > 0:
                    neighbors.append(grid[i, j - 1])
                if j < cols - 1:
                    neighbors.append(grid[i, j + 1])

                new_grid[i, j] = sum(neighbors) / len(neighbors)

        grid = new_grid

    return grid


def generate_pressure_field(params: dict) -> np.ndarray:
    """
    Generate initial pressure field before constraints.
    """

    # 1. Base longitudinal distribution
    profile = _base_longitudinal_profile()

    # 2. Structural redistribution
    profile = _apply_arch_bias(profile, params["arch_bias"])

    # 3. Expand to 2D sole grid
    grid = _expand_to_grid(profile)

    # 4. Apply contact capacity shaping
    grid = _apply_contact_capacity(
        grid,
        params["contact_capacity"]
    )

    # 5. Bounded smoothing based on stiffness
    grid = _smooth_grid_bounded(
        grid,
        params["stiffness_factor"]
    )

    return grid
