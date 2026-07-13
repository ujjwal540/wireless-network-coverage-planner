"""
visualization.py
=================
All Matplotlib rendering for the planner: heatmaps, filled signal
contours, coverage-radius maps, path-loss curves, obstacle site plans
and a combined dashboard. A dark "RF planning tool" theme is used
throughout for a professional, industry-style look.
"""

import os

import numpy as np

# Keep Matplotlib's generated font cache in the project so the planner also
# works when the user profile directory is read-only.
os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.path.dirname(__file__), ".matplotlib"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap

from propagation import max_coverage_radius, path_loss

plt.style.use("dark_background")

# Signal-strength colormap: deep blue (weak) -> cyan -> yellow -> red (strong)
RF_CMAP = LinearSegmentedColormap.from_list(
    "rf_signal",
    ["#08172a", "#0b3d91", "#1f78b4", "#33a1c9", "#7fd858",
     "#f4d03f", "#f39c12", "#e74c3c", "#ff2d55"],
)

FIG_FACE = "#0d1117"
AX_FACE = "#0d1117"
GRID_COLOR = "#30363d"


def _style_axes(ax, title, xlabel="X (meters)", ylabel="Y (meters)"):
    ax.set_title(title, fontsize=13, weight="bold", color="white", pad=10)
    ax.set_xlabel(xlabel, color="#c9d1d9")
    ax.set_ylabel(ylabel, color="#c9d1d9")
    ax.tick_params(colors="#8b949e")
    for spine in ax.spines.values():
        spine.set_color("#30363d")


def _draw_obstacles(ax, obstacles):
    for obs in obstacles:
        rect = patches.Rectangle(
            (obs.x, obs.y), obs.width, obs.height,
            linewidth=1.2, edgecolor="#f0f0f0",
            facecolor="#2b2f36", alpha=0.85, zorder=5, hatch="////",
        )
        ax.add_patch(rect)
        cx, cy = obs.x + obs.width / 2, obs.y + obs.height / 2
        rotation = 90 if obs.height > obs.width * 2 else 0
        ax.text(cx, cy, f"{obs.name}\n(-{obs.attenuation_db:.0f} dB)",
                 fontsize=5.5, color="#f0f0f0", ha="center", va="center",
                 rotation=rotation, zorder=6, weight="bold")


def _draw_transmitters(ax, transmitters, small=False):
    fs = 6.5 if small else 8
    for tx in transmitters:
        ax.plot(tx.x, tx.y, marker="^", markersize=13 if not small else 9,
                 color="#39ff14", markeredgecolor="black", markeredgewidth=1.1,
                 zorder=10)
        label = f"{tx.name}\n{tx.power_dbm:.0f}dBm | {tx.frequency_mhz:.0f}MHz"
        ax.annotate(label, (tx.x, tx.y), textcoords="offset points", xytext=(9, 9),
                     fontsize=fs, color="white", weight="bold",
                     bbox=dict(boxstyle="round,pad=0.25", fc="black", ec="#39ff14", alpha=0.75),
                     zorder=11)


# ---------------------------------------------------------------------------
# 1. Signal-strength heatmap
# ---------------------------------------------------------------------------
def plot_heatmap(xs, ys, grid, transmitters, obstacles, config, save_path,
                  title="Wi-Fi / Base Station Signal Heatmap"):
    fig, ax = plt.subplots(figsize=(10, 7.5), facecolor=FIG_FACE)
    ax.set_facecolor(AX_FACE)

    im = ax.imshow(grid, extent=[xs[0], xs[-1], ys[0], ys[-1]], origin="lower",
                    cmap=RF_CMAP, vmin=-100, vmax=-25, aspect="equal", zorder=1)
    cbar = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
    cbar.set_label("Received Signal Strength (dBm)", color="white")
    cbar.ax.yaxis.set_tick_params(color="#8b949e")
    plt.setp(cbar.ax.get_yticklabels(), color="#c9d1d9")

    _draw_obstacles(ax, obstacles)
    _draw_transmitters(ax, transmitters)
    _style_axes(ax, title)
    fig.tight_layout()
    fig.savefig(save_path, dpi=160, facecolor=FIG_FACE)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Filled contour "signal strength" plot (discrete RF bands)
# ---------------------------------------------------------------------------
def plot_signal_contour(xs, ys, grid, transmitters, obstacles, config, save_path,
                         title="Signal Strength Contours"):
    fig, ax = plt.subplots(figsize=(10, 7.5), facecolor=FIG_FACE)
    ax.set_facecolor(AX_FACE)

    X, Y = np.meshgrid(xs, ys)
    levels = [-100, -90, -80, -75, -70, -60, -50, -40, -25]
    cf = ax.contourf(X, Y, grid, levels=levels, cmap=RF_CMAP, extend="both", zorder=1)
    cs = ax.contour(X, Y, grid, levels=levels, colors="black", linewidths=0.3, alpha=0.5, zorder=2)
    cbar = fig.colorbar(cf, ax=ax, shrink=0.85, pad=0.02)
    cbar.set_label("Signal Strength (dBm)", color="white")
    plt.setp(cbar.ax.get_yticklabels(), color="#c9d1d9")

    _draw_obstacles(ax, obstacles)
    _draw_transmitters(ax, transmitters)
    _style_axes(ax, title)
    fig.tight_layout()
    fig.savefig(save_path, dpi=160, facecolor=FIG_FACE)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Coverage radius / binary coverage map
# ---------------------------------------------------------------------------
def plot_coverage_radius(xs, ys, grid, covered, transmitters, obstacles, config,
                          save_path, coverage_pct, title="Coverage Radius Map"):
    fig, ax = plt.subplots(figsize=(10, 7.5), facecolor=FIG_FACE)
    ax.set_facecolor(AX_FACE)

    cov_cmap = LinearSegmentedColormap.from_list("cov", ["#2b0a0a", "#124e0b"])
    ax.imshow(covered, extent=[xs[0], xs[-1], ys[0], ys[-1]], origin="lower",
              cmap=cov_cmap, alpha=0.9, aspect="equal", zorder=1)

    # theoretical (obstacle-free) coverage circles
    for tx in transmitters:
        r = max_coverage_radius(tx.eirp_dbm(), config.RX_SENSITIVITY_DBM, tx.frequency_mhz,
                                 config.PATH_LOSS_MODEL, config.PATH_LOSS_EXPONENT,
                                 config.REFERENCE_DISTANCE)
        circle = patches.Circle((tx.x, tx.y), r, fill=False, edgecolor="#39ff14",
                                  linewidth=1.6, linestyle="--", alpha=0.9, zorder=8)
        ax.add_patch(circle)
        ax.text(tx.x, tx.y - r - 2.5, f"r ≈ {r:.1f} m", color="#39ff14",
                 fontsize=7.5, ha="center", weight="bold", zorder=9)

    _draw_obstacles(ax, obstacles)
    _draw_transmitters(ax, transmitters)
    _style_axes(ax, f"{title}  |  Covered area: {coverage_pct:.1f}% "
                     f"(≥ {config.RX_SENSITIVITY_DBM} dBm)")

    green_patch = patches.Patch(color="#124e0b", label=f"Covered (≥ {config.RX_SENSITIVITY_DBM} dBm)")
    red_patch = patches.Patch(color="#2b0a0a", label="Not covered")
    dash_line = matplotlib.lines.Line2D([0], [0], color="#39ff14", linestyle="--",
                                          label="Theoretical LOS radius")
    ax.legend(handles=[green_patch, red_patch, dash_line], loc="upper right",
              fontsize=7.5, facecolor="#161b22", edgecolor="#30363d", labelcolor="white")

    fig.tight_layout()
    fig.savefig(save_path, dpi=160, facecolor=FIG_FACE)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 4. Path-loss vs distance curves
# ---------------------------------------------------------------------------
def plot_path_loss(transmitters, config, save_path, title="Path Loss vs. Distance"):
    fig, ax = plt.subplots(figsize=(9, 6), facecolor=FIG_FACE)
    ax.set_facecolor(AX_FACE)

    d = np.linspace(1, 150, 300)
    colors = ["#39ff14", "#ff2d55", "#33a1c9", "#f4d03f", "#f39c12"]

    freqs_seen = {}
    for tx in transmitters:
        freqs_seen.setdefault(tx.frequency_mhz, tx.name)

    for i, (freq, name) in enumerate(freqs_seen.items()):
        c = colors[i % len(colors)]
        fspl_curve = [path_loss(x, freq, "fspl") for x in d]
        log_curve = [path_loss(x, freq, "log_distance", config.PATH_LOSS_EXPONENT,
                                 config.REFERENCE_DISTANCE) for x in d]
        ax.plot(d, fspl_curve, color=c, linestyle=":", linewidth=1.8,
                 label=f"{freq:.0f} MHz — Free Space (FSPL)")
        ax.plot(d, log_curve, color=c, linestyle="-", linewidth=2.2,
                 label=f"{freq:.0f} MHz — Log-Distance (n={config.PATH_LOSS_EXPONENT})")

    ax.axhline(y=0, color=GRID_COLOR, linewidth=0.5)
    ax.grid(True, color=GRID_COLOR, linewidth=0.6, alpha=0.6)
    _style_axes(ax, title, xlabel="Distance (meters)", ylabel="Path Loss (dB)")
    ax.legend(fontsize=8, facecolor="#161b22", edgecolor="#30363d", labelcolor="white", loc="lower right")
    fig.tight_layout()
    fig.savefig(save_path, dpi=160, facecolor=FIG_FACE)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Obstacle / site plan (no signal overlay)
# ---------------------------------------------------------------------------
def plot_obstacles(transmitters, obstacles, config, save_path, title="Site Plan — Transmitters & Obstacles"):
    fig, ax = plt.subplots(figsize=(10, 7.5), facecolor=FIG_FACE)
    ax.set_facecolor(AX_FACE)

    ax.set_xlim(0, config.GRID_WIDTH)
    ax.set_ylim(0, config.GRID_HEIGHT)
    ax.set_aspect("equal")
    ax.grid(True, color=GRID_COLOR, linewidth=0.4, alpha=0.5)

    _draw_obstacles(ax, obstacles)
    _draw_transmitters(ax, transmitters)
    _style_axes(ax, title)
    fig.tight_layout()
    fig.savefig(save_path, dpi=160, facecolor=FIG_FACE)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 6. Combined dashboard (2x2)
# ---------------------------------------------------------------------------
def plot_dashboard(xs, ys, grid, covered, transmitters, obstacles, config,
                    coverage_pct, save_path):
    fig, axes = plt.subplots(2, 2, figsize=(15, 11), facecolor=FIG_FACE)
    fig.suptitle("Wireless Network Coverage Planner — Simulation Dashboard",
                 fontsize=16, weight="bold", color="white", y=0.98)

    # -- Heatmap (top-left)
    ax = axes[0, 0]
    ax.set_facecolor(AX_FACE)
    im = ax.imshow(grid, extent=[xs[0], xs[-1], ys[0], ys[-1]], origin="lower",
                    cmap=RF_CMAP, vmin=-100, vmax=-25, aspect="equal", zorder=1)
    fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02).set_label("dBm", color="white")
    _draw_obstacles(ax, obstacles)
    _draw_transmitters(ax, transmitters, small=True)
    _style_axes(ax, "Signal Heatmap")

    # -- Coverage radius (top-right)
    ax = axes[0, 1]
    ax.set_facecolor(AX_FACE)
    cov_cmap = LinearSegmentedColormap.from_list("cov", ["#2b0a0a", "#124e0b"])
    ax.imshow(covered, extent=[xs[0], xs[-1], ys[0], ys[-1]], origin="lower",
              cmap=cov_cmap, alpha=0.9, aspect="equal", zorder=1)
    for tx in transmitters:
        r = max_coverage_radius(tx.eirp_dbm(), config.RX_SENSITIVITY_DBM, tx.frequency_mhz,
                                 config.PATH_LOSS_MODEL, config.PATH_LOSS_EXPONENT,
                                 config.REFERENCE_DISTANCE)
        ax.add_patch(patches.Circle((tx.x, tx.y), r, fill=False, edgecolor="#39ff14",
                                      linewidth=1.4, linestyle="--", alpha=0.9, zorder=8))
    _draw_obstacles(ax, obstacles)
    _draw_transmitters(ax, transmitters, small=True)
    _style_axes(ax, f"Coverage: {coverage_pct:.1f}% ≥ {config.RX_SENSITIVITY_DBM} dBm")

    # -- Path loss (bottom-left)
    ax = axes[1, 0]
    ax.set_facecolor(AX_FACE)
    d = np.linspace(1, 150, 300)
    colors = ["#39ff14", "#ff2d55", "#33a1c9", "#f4d03f"]
    freqs_seen = {}
    for tx in transmitters:
        freqs_seen.setdefault(tx.frequency_mhz, tx.name)
    for i, freq in enumerate(freqs_seen):
        c = colors[i % len(colors)]
        ax.plot(d, [path_loss(x, freq, "fspl") for x in d], color=c, linestyle=":",
                 linewidth=1.6, label=f"{freq:.0f}MHz FSPL")
        ax.plot(d, [path_loss(x, freq, "log_distance", config.PATH_LOSS_EXPONENT) for x in d],
                 color=c, linestyle="-", linewidth=2, label=f"{freq:.0f}MHz Log-Dist")
    ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.6)
    _style_axes(ax, "Path Loss Models", xlabel="Distance (m)", ylabel="Loss (dB)")
    ax.legend(fontsize=7, facecolor="#161b22", edgecolor="#30363d", labelcolor="white")

    # -- Site plan (bottom-right)
    ax = axes[1, 1]
    ax.set_facecolor(AX_FACE)
    ax.set_xlim(0, config.GRID_WIDTH)
    ax.set_ylim(0, config.GRID_HEIGHT)
    ax.set_aspect("equal")
    ax.grid(True, color=GRID_COLOR, linewidth=0.4, alpha=0.5)
    _draw_obstacles(ax, obstacles)
    _draw_transmitters(ax, transmitters, small=True)
    _style_axes(ax, "Site Plan")

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(save_path, dpi=150, facecolor=FIG_FACE)
    plt.close(fig)
