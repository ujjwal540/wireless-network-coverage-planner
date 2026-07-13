"""
heatmap.py
==========
Builds the 2-D received-signal-strength grid over the whole site by
evaluating every transmitter at every grid point, applying path loss
and obstacle attenuation, and keeping the strongest ("best server")
signal at each point -- exactly how a real multi-AP coverage map is
produced.
"""

import numpy as np

from utils import euclidean_distance
from obstacles import calculate_obstacle_loss
from propagation import received_power

NO_SIGNAL_DBM = -150.0  # floor value where no transmitter reaches


def build_signal_grid(transmitters, obstacles, config):
    """
    Returns:
        xs, ys : 1-D coordinate arrays (meters)
        grid   : 2-D array [len(ys), len(xs)] of best received signal (dBm)
        server : 2-D array [len(ys), len(xs)] of the index of the serving
                 transmitter at each point (-1 if none)
    """
    xs = np.arange(0, config.GRID_WIDTH, config.RESOLUTION)
    ys = np.arange(0, config.GRID_HEIGHT, config.RESOLUTION)

    grid = np.full((len(ys), len(xs)), NO_SIGNAL_DBM)
    server = np.full((len(ys), len(xs)), -1, dtype=int)

    for yi, y in enumerate(ys):
        for xi, x in enumerate(xs):
            best_rx = NO_SIGNAL_DBM
            best_tx = -1
            for ti, tx in enumerate(transmitters):
                dist = euclidean_distance(tx.x, tx.y, x, y)
                obs_loss, _ = calculate_obstacle_loss(tx.x, tx.y, x, y, obstacles)
                rx = received_power(
                    tx.eirp_dbm(), dist, tx.frequency_mhz, obs_loss,
                    config.PATH_LOSS_MODEL, config.PATH_LOSS_EXPONENT,
                    config.REFERENCE_DISTANCE,
                )
                if rx > best_rx:
                    best_rx = rx
                    best_tx = ti
            grid[yi, xi] = best_rx
            server[yi, xi] = best_tx

    return xs, ys, grid, server
