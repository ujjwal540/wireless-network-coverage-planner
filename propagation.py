"""
propagation.py
==============
RF propagation / path-loss models used to translate distance (and
obstacles) into received signal strength.

Models implemented:
  * Free Space Path Loss (FSPL)   - ideal, no obstructions
  * Log-Distance Path Loss        - standard indoor/urban model that
                                     generalises FSPL with a tunable
                                     path-loss exponent `n`
"""

import numpy as np


def free_space_path_loss(distance_m, frequency_mhz):
    """
    Free Space Path Loss (dB):
        FSPL(dB) = 20*log10(d_km) + 20*log10(f_MHz) + 32.44
    """
    d_km = max(distance_m, 0.1) / 1000.0
    return 20 * np.log10(d_km) + 20 * np.log10(frequency_mhz) + 32.44


def log_distance_path_loss(distance_m, frequency_mhz, n=3.0, d0=1.0):
    """
    Log-Distance Path Loss model:
        PL(d) = PL(d0) + 10*n*log10(d/d0)
    where PL(d0) is the free-space loss at the reference distance d0,
    and n is the path-loss exponent (2 = free space, 3 = office,
    4-5 = dense/concrete environments).
    """
    d = max(distance_m, 0.1)
    pl_d0 = free_space_path_loss(d0, frequency_mhz)
    return pl_d0 + 10 * n * np.log10(d / d0)


def path_loss(distance_m, frequency_mhz, model="log_distance", n=3.0, d0=1.0):
    """Dispatch to the selected path-loss model."""
    if model == "fspl":
        return free_space_path_loss(distance_m, frequency_mhz)
    elif model == "log_distance":
        return log_distance_path_loss(distance_m, frequency_mhz, n, d0)
    raise ValueError(f"Unknown path loss model: {model}")


def received_power(tx_eirp_dbm, distance_m, frequency_mhz, obstacle_loss_db=0.0,
                    model="log_distance", n=3.0, d0=1.0):
    """
    Received signal strength (dBm) at a point:
        Rx = EIRP - PathLoss(distance) - ObstacleLoss
    """
    pl = path_loss(distance_m, frequency_mhz, model, n, d0)
    return tx_eirp_dbm - pl - obstacle_loss_db


def max_coverage_radius(eirp_dbm, threshold_dbm, frequency_mhz,
                         model="log_distance", n=3.0, d0=1.0):
    """
    Solve the path-loss model for the distance at which received power
    drops to `threshold_dbm`, assuming a clear line of sight (no
    obstacles). This gives the theoretical maximum coverage radius used
    to draw reference circles on the coverage map.
    """
    budget = eirp_dbm - threshold_dbm  # dB of loss the link can tolerate
    if model == "fspl":
        d_km = 10 ** ((budget - 20 * np.log10(frequency_mhz) - 32.44) / 20)
        return max(d_km * 1000.0, 0.0)
    elif model == "log_distance":
        pl_d0 = free_space_path_loss(d0, frequency_mhz)
        d = d0 * 10 ** ((budget - pl_d0) / (10 * n))
        return max(d, 0.0)
    raise ValueError(f"Unknown path loss model: {model}")
