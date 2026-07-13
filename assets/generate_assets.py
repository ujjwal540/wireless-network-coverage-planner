"""
generate_assets.py
===================
One-off helper that generates the branding / reference images stored in
assets/ (logo.png, floor_plan.png, office_map.png). Not required to run
the simulator -- kept here only so the images in assets/ are reproducible.

Run with:  python assets/generate_assets.py
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
plt.style.use("dark_background")

HERE = os.path.dirname(os.path.abspath(__file__))


def make_logo():
    fig, ax = plt.subplots(figsize=(4, 4), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.axis("off")
    for r, a in zip([0.35, 0.6, 0.85], [1.0, 0.6, 0.3]):
        arc = patches.Arc((0, -0.15), r * 2, r * 2, angle=0, theta1=35, theta2=145,
                            color="#39ff14", linewidth=4, alpha=a)
        ax.add_patch(arc)
    ax.plot(0, -0.15, marker="^", markersize=22, color="#39ff14", markeredgecolor="white")
    ax.text(0, -0.85, "WNCP", ha="center", fontsize=22, weight="bold", color="white")
    fig.savefig(os.path.join(HERE, "logo.png"), dpi=200, facecolor="#0d1117", bbox_inches="tight")
    plt.close(fig)


def make_floor_plan():
    fig, ax = plt.subplots(figsize=(10, 7.5), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 90)
    ax.set_aspect("equal")
    ax.add_patch(patches.Rectangle((0, 0), 120, 90, fill=False, edgecolor="white", linewidth=2))
    rooms = [
        (2, 2, 36, 40, "Open Office West"),
        (44, 2, 74, 44, "Open Office East"),
        (2, 58, 22, 30, "Meeting Rooms"),
        (30, 58, 46, 30, "Break Area"),
        (80, 50, 38, 38, "Server / IT Room"),
    ]
    for x, y, w, h, label in rooms:
        ax.add_patch(patches.Rectangle((x, y), w, h, fill=False, edgecolor="#8b949e", linewidth=1))
        ax.text(x + w / 2, y + h / 2, label, color="#c9d1d9", ha="center", fontsize=8)
    ax.set_title("Reference Floor Plan", color="white", weight="bold")
    ax.axis("off")
    fig.savefig(os.path.join(HERE, "floor_plan.png"), dpi=160, facecolor="#0d1117", bbox_inches="tight")
    plt.close(fig)


def make_office_map():
    fig, ax = plt.subplots(figsize=(10, 7.5), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 90)
    ax.set_aspect("equal")
    ax.add_patch(patches.Rectangle((0, 0), 120, 90, fill=False, edgecolor="white", linewidth=2))
    desks = [(x, y) for x in range(10, 110, 12) for y in range(10, 80, 14)]
    for (x, y) in desks:
        ax.add_patch(patches.Rectangle((x, y), 6, 3, facecolor="#30363d", edgecolor="#8b949e"))
    ax.set_title("Reference Office Desk Map", color="white", weight="bold")
    ax.axis("off")
    fig.savefig(os.path.join(HERE, "office_map.png"), dpi=160, facecolor="#0d1117", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    make_logo()
    make_floor_plan()
    make_office_map()
    print("Assets generated in", HERE)
