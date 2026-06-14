"""
sun_utils.py — sun-avoidance geometry helpers.

  path_crosses_sun(fx, fy, tx, ty)      -> bool
  sun_cross_mask_tensor(sx, sy, tx, ty) -> BoolTensor [S, T]

The sun is fixed at (50, 50) with radius 10.
SUN_MARGIN adds a safety buffer; 1.0 is conservative because planets
drift orbitally, so straight-line distances slightly underestimate
the true closest approach on a curved path.
"""

import math
import torch
from torch import Tensor

CENTER_X   = 50.0
CENTER_Y   = 50.0
SUN_RADIUS = 10.0
SUN_MARGIN =  1.0


def _segment_min_dist_scalar(ax, ay, bx, by, px, py) -> float:
    """Minimum distance from segment AB to point P (pure Python, no torch)."""
    dx, dy = bx - ax, by - ay
    len2   = dx * dx + dy * dy
    if len2 == 0:
        return math.hypot(ax - px, ay - py)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / len2))
    return math.hypot(ax + t * dx - px, ay + t * dy - py)


def path_crosses_sun(fx: float, fy: float, tx: float, ty: float) -> bool:
    """Return True if the straight-line path from (fx,fy) to (tx,ty) crosses the sun."""
    return _segment_min_dist_scalar(fx, fy, tx, ty, CENTER_X, CENTER_Y) <= SUN_RADIUS + SUN_MARGIN


def sun_cross_mask_tensor(sx: Tensor, sy: Tensor, tx: Tensor, ty: Tensor) -> Tensor:
    """
    Vectorised path_crosses_sun for all (source, target) pairs.

    Args:
        sx, sy : source coordinates  [S]
        tx, ty : target coordinates  [T]

    Returns:
        BoolTensor [S, T] — True where path CROSSES the sun (= invalid launch).
    """
    S, T = sx.shape[0], tx.shape[0]

    ax = sx.view(S, 1).expand(S, T)
    ay = sy.view(S, 1).expand(S, T)
    bx = tx.view(1, T).expand(S, T)
    by = ty.view(1, T).expand(S, T)

    px        = torch.tensor(CENTER_X, dtype=ax.dtype, device=ax.device)
    py        = torch.tensor(CENTER_Y, dtype=ay.dtype, device=ay.device)
    threshold = SUN_RADIUS + SUN_MARGIN

    dx   = bx - ax
    dy   = by - ay
    len2 = (dx * dx + dy * dy).clamp(min=1e-9)

    t = ((px - ax) * dx + (py - ay) * dy) / len2
    t = t.clamp(0.0, 1.0)

    closest_x = ax + t * dx
    closest_y = ay + t * dy

    min_dist = torch.sqrt((closest_x - px) ** 2 + (closest_y - py) ** 2)
    return min_dist <= threshold   # True = crosses sun = INVALID
