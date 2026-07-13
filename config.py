"""
config.py
=========
Central configuration for the Wireless Network Coverage Planner.
Edit the values below to model your own site (dimensions, transmitters,
obstacles, and radio parameters) without touching any simulation code.
"""

# ---------------------------------------------------------------------------
# Environment / Grid
# ---------------------------------------------------------------------------
GRID_WIDTH = 120.0        # site width in meters (X axis)
GRID_HEIGHT = 90.0        # site height in meters (Y axis)
RESOLUTION = 1.0          # meters per grid cell (lower = higher fidelity, slower)

# ---------------------------------------------------------------------------
# Radio-frequency parameters
# ---------------------------------------------------------------------------
FREQUENCY_MHZ = 2400              # default carrier frequency (2.4 GHz Wi-Fi)
PATH_LOSS_MODEL = "log_distance"  # "fspl" (free space) or "log_distance" (indoor)
PATH_LOSS_EXPONENT = 3.0          # n: 2=free space, 3=office, 4-5=dense/concrete
REFERENCE_DISTANCE = 1.0          # d0 in meters for the log-distance model

# ---------------------------------------------------------------------------
# Coverage threshold
# ---------------------------------------------------------------------------
RX_SENSITIVITY_DBM = -75          # minimum usable signal strength (dBm)

# ---------------------------------------------------------------------------
# Transmitters (APs / Base Stations)
# ---------------------------------------------------------------------------
TRANSMITTERS = [
    {"name": "AP-1", "x": 22, "y": 22, "power_dbm": 20, "antenna_gain_dbi": 2.0, "frequency_mhz": 2400},
    {"name": "AP-2", "x": 92, "y": 68, "power_dbm": 18, "antenna_gain_dbi": 3.0, "frequency_mhz": 5000},
    {"name": "AP-3", "x": 20, "y": 72, "power_dbm": 16, "antenna_gain_dbi": 2.0, "frequency_mhz": 2400},
]

# ---------------------------------------------------------------------------
# Obstacles (walls, doors, partitions...) -- axis-aligned rectangles
# attenuation_db = signal loss (dB) incurred each time a ray crosses it
# ---------------------------------------------------------------------------
OBSTACLES = [
    {"name": "Concrete Wall A",  "x": 40, "y": 0,  "width": 2,  "height": 40, "attenuation_db": 12},
    {"name": "Concrete Wall B",  "x": 40, "y": 50, "width": 2,  "height": 40, "attenuation_db": 12},
    {"name": "Glass Partition",  "x": 65, "y": 15, "width": 18, "height": 2,  "attenuation_db": 4},
    {"name": "Drywall Office",   "x": 10, "y": 55, "width": 26, "height": 2,  "attenuation_db": 5},
    {"name": "Metal Fire Door",  "x": 58, "y": 38, "width": 3,  "height": 3,  "attenuation_db": 15},
    {"name": "Elevator Shaft",   "x": 96, "y": 8,  "width": 9,  "height": 9,  "attenuation_db": 20},
    {"name": "Server Room Wall", "x": 78, "y": 45, "width": 2,  "height": 30, "attenuation_db": 14},
]

# ---------------------------------------------------------------------------
# Output locations
# ---------------------------------------------------------------------------
OUTPUT_DIR = "outputs"
SCREENSHOT_DIR = "screenshots"
ASSETS_DIR = "assets"
