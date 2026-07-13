"""
obstacles.py
============
Models physical obstructions (walls, doors, partitions, shafts) as
axis-aligned rectangles, each with a signal attenuation value in dB.

Obstacle loss between a transmitter and a receiver point is computed by
testing the direct ray between them against every obstacle rectangle
using the Liang-Barsky line-clipping algorithm, and summing the
attenuation of every rectangle the ray passes through.
"""


class Obstacle:
    def __init__(self, name, x, y, width, height, attenuation_db):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.attenuation_db = float(attenuation_db)

    @property
    def bounds(self):
        """Return (xmin, xmax, ymin, ymax)."""
        return self.x, self.x + self.width, self.y, self.y + self.height

    def __repr__(self):
        return f"<Obstacle {self.name} {self.width}x{self.height}m -{self.attenuation_db}dB>"

    @staticmethod
    def from_config(entries):
        """Build a list of Obstacle objects from config.OBSTACLES."""
        return [Obstacle(**e) for e in entries]


def _segment_intersects_rect(x1, y1, x2, y2, xmin, xmax, ymin, ymax):
    """
    Liang-Barsky line-clipping test.
    Returns True if the segment (x1,y1)-(x2,y2) enters the rectangle
    [xmin,xmax] x [ymin,ymax] for any nonzero-length portion.
    """
    dx = x2 - x1
    dy = y2 - y1
    p = (-dx, dx, -dy, dy)
    q = (x1 - xmin, xmax - x1, y1 - ymin, ymax - y1)

    t0, t1 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return False  # parallel and outside
        else:
            r = qi / pi
            if pi < 0:
                if r > t1:
                    return False
                if r > t0:
                    t0 = r
            else:
                if r < t0:
                    return False
                if r < t1:
                    t1 = r
    return t0 < t1


def calculate_obstacle_loss(x1, y1, x2, y2, obstacles):
    """
    Sum the attenuation (dB) of every obstacle whose rectangle is crossed
    by the direct ray from (x1,y1) to (x2,y2).

    Returns (total_loss_db, list_of_obstacle_names_crossed).
    """
    total_loss = 0.0
    crossed = []
    for obs in obstacles:
        xmin, xmax, ymin, ymax = obs.bounds
        if _segment_intersects_rect(x1, y1, x2, y2, xmin, xmax, ymin, ymax):
            total_loss += obs.attenuation_db
            crossed.append(obs.name)
    return total_loss, crossed
