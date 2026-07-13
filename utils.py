"""
utils.py
========
Small, dependency-free helper functions shared across the project:
unit conversions, geometry helpers, filesystem helpers and CSV export.
"""

import csv
import os
import numpy as np


def dbm_to_mw(dbm):
    """Convert power in dBm to milliwatts."""
    return 10 ** (dbm / 10.0)


def mw_to_dbm(mw):
    """Convert power in milliwatts to dBm."""
    return 10 * np.log10(mw)


def euclidean_distance(x1, y1, x2, y2):
    """Straight-line distance between two points in meters."""
    return float(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))


def ensure_dir(path):
    """Create a directory (and parents) if it does not already exist."""
    if path:
        os.makedirs(path, exist_ok=True)


def export_csv(records, path, header):
    """Write a list of row-tuples to a CSV file, creating folders as needed."""
    ensure_dir(os.path.dirname(path))
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(records)
