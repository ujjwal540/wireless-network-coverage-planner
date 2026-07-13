"""
simulator.py
============
Ties the whole pipeline together:
  config -> transmitters + obstacles -> signal grid -> visuals + CSV report
"""

import os

from transmitter import Transmitter
from obstacles import Obstacle
from heatmap import build_signal_grid
from utils import ensure_dir, export_csv
import visualization as viz


class Simulator:
    def __init__(self, cfg):
        self.cfg = cfg
        self.transmitters = Transmitter.from_config(cfg.TRANSMITTERS)
        self.obstacles = Obstacle.from_config(cfg.OBSTACLES)
        self.xs = self.ys = self.grid = self.server = None

    # -- Step 1-6: build environment grid, compute distance/path-loss/obstacle loss, signal --
    def run(self):
        print(f"[Simulator] Building {self.cfg.GRID_WIDTH:.0f}x{self.cfg.GRID_HEIGHT:.0f} m "
              f"grid @ {self.cfg.RESOLUTION} m resolution "
              f"({len(self.transmitters)} transmitters, {len(self.obstacles)} obstacles)...")
        self.xs, self.ys, self.grid, self.server = build_signal_grid(
            self.transmitters, self.obstacles, self.cfg
        )
        print("[Simulator] Signal strength grid complete.")
        return self.xs, self.ys, self.grid, self.server

    def coverage_stats(self):
        covered = self.grid >= self.cfg.RX_SENSITIVITY_DBM
        pct = 100.0 * covered.sum() / covered.size
        return covered, pct

    # -- Step 7-9: heatmap, coverage radius, export --
    def export_all(self):
        ensure_dir(self.cfg.OUTPUT_DIR)
        ensure_dir(self.cfg.SCREENSHOT_DIR)
        out, shot = self.cfg.OUTPUT_DIR, self.cfg.SCREENSHOT_DIR

        viz.plot_heatmap(self.xs, self.ys, self.grid, self.transmitters, self.obstacles,
                          self.cfg, os.path.join(out, "heatmap.png"))
        viz.plot_heatmap(self.xs, self.ys, self.grid, self.transmitters, self.obstacles,
                          self.cfg, os.path.join(shot, "heatmap.png"))

        viz.plot_signal_contour(self.xs, self.ys, self.grid, self.transmitters, self.obstacles,
                                 self.cfg, os.path.join(out, "signal_strength.png"))

        covered, pct = self.coverage_stats()
        viz.plot_coverage_radius(self.xs, self.ys, self.grid, covered, self.transmitters,
                                  self.obstacles, self.cfg, os.path.join(out, "coverage_radius.png"), pct)
        viz.plot_coverage_radius(self.xs, self.ys, self.grid, covered, self.transmitters,
                                  self.obstacles, self.cfg, os.path.join(shot, "coverage.png"), pct)

        viz.plot_path_loss(self.transmitters, self.cfg, os.path.join(out, "path_loss.png"))
        viz.plot_path_loss(self.transmitters, self.cfg, os.path.join(shot, "propagation.png"))

        viz.plot_obstacles(self.transmitters, self.obstacles, self.cfg,
                            os.path.join(shot, "obstacles.png"))

        viz.plot_dashboard(self.xs, self.ys, self.grid, covered, self.transmitters,
                            self.obstacles, self.cfg, pct, os.path.join(shot, "dashboard.png"))

        self._export_csv_report(covered, out)
        print(f"[Simulator] All visuals exported to ./{out}/ and ./{shot}/")
        return pct

    def _export_csv_report(self, covered, out_dir):
        records = []
        for yi, y in enumerate(self.ys):
            for xi, x in enumerate(self.xs):
                tx_idx = self.server[yi, xi]
                tx_name = self.transmitters[tx_idx].name if tx_idx >= 0 else "None"
                records.append([
                    round(float(x), 2), round(float(y), 2), tx_name,
                    round(float(self.grid[yi, xi]), 2),
                    bool(covered[yi, xi]),
                ])
        header = ["x_m", "y_m", "best_server", "signal_dbm", "covered"]
        export_csv(records, os.path.join(out_dir, "simulation_report.csv"), header)
        print(f"[Simulator] CSV report exported ({len(records)} grid points).")
