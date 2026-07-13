"""
main.py
=======
Command-line entry point for the Wireless Network Coverage Planner.

Usage:
    python main.py
    python main.py --model fspl --threshold -70
    python main.py --width 150 --height 100 --resolution 0.5
"""

import argparse

import config
from simulator import Simulator
from propagation import max_coverage_radius


def parse_args():
    p = argparse.ArgumentParser(description="Wireless Network (Wi-Fi/Base Station) Coverage Planner")
    p.add_argument("--width", type=float, default=config.GRID_WIDTH, help="site width in meters")
    p.add_argument("--height", type=float, default=config.GRID_HEIGHT, help="site height in meters")
    p.add_argument("--resolution", type=float, default=config.RESOLUTION, help="grid resolution in meters")
    p.add_argument("--model", choices=["fspl", "log_distance"], default=config.PATH_LOSS_MODEL,
                   help="path-loss model to use")
    p.add_argument("--exponent", type=float, default=config.PATH_LOSS_EXPONENT,
                   help="path-loss exponent n (log-distance model only)")
    p.add_argument("--threshold", type=float, default=config.RX_SENSITIVITY_DBM,
                   help="minimum usable signal strength in dBm")
    return p.parse_args()


def main():
    args = parse_args()
    config.GRID_WIDTH = args.width
    config.GRID_HEIGHT = args.height
    config.RESOLUTION = args.resolution
    config.PATH_LOSS_MODEL = args.model
    config.PATH_LOSS_EXPONENT = args.exponent
    config.RX_SENSITIVITY_DBM = args.threshold

    print("=" * 64)
    print(" WIRELESS NETWORK COVERAGE PLANNER")
    print("=" * 64)
    print(f" Area            : {config.GRID_WIDTH:.0f} x {config.GRID_HEIGHT:.0f} m")
    print(f" Resolution      : {config.RESOLUTION} m/cell")
    print(f" Path-loss model : {config.PATH_LOSS_MODEL} (n={config.PATH_LOSS_EXPONENT})")
    print(f" Rx sensitivity  : {config.RX_SENSITIVITY_DBM} dBm")
    print("-" * 64)

    sim = Simulator(config)
    sim.run()
    pct = sim.export_all()

    print("-" * 64)
    print(" TRANSMITTER SUMMARY")
    for tx in sim.transmitters:
        r = max_coverage_radius(tx.eirp_dbm(), config.RX_SENSITIVITY_DBM, tx.frequency_mhz,
                                 config.PATH_LOSS_MODEL, config.PATH_LOSS_EXPONENT,
                                 config.REFERENCE_DISTANCE)
        print(f"  {tx.name:8s}  EIRP={tx.eirp_dbm():5.1f} dBm   "
              f"{tx.frequency_mhz:5.0f} MHz   theoretical radius ~= {r:6.1f} m")
    print("-" * 64)
    print(f" Overall coverage : {pct:.1f}% of area >= {config.RX_SENSITIVITY_DBM} dBm")
    print(f" Outputs saved to : ./{config.OUTPUT_DIR}/  and  ./{config.SCREENSHOT_DIR}/")
    print("=" * 64)


if __name__ == "__main__":
    main()
