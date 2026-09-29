"""make_schemas.py — schematic figures Fig.1/Fig.2/Fig.3 for the paper."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")


# ---------------- Fig 1: overall workflow ----------------
def fig1():
    fig, ax = plt.subplots(figsize=(9, 2.6))
    ax.axis("off")
    boxes = [
        ("TMM physical\nforward model", "#dbe9f6"),
        ("5000 thickness–\nspectrum data", "#e6f4e6"),
        ("MLP surrogate\n(4-128-128-64-41)", "#fde9d9"),
        ("10000 candidates\nfast screening", "#f3e6f4"),
        ("TMM re-verify\nTop-5 design", "#fde0e0"),
    ]
    w, h, gap = 1.5, 1.0, 0.35
    x = 0.0
    for i, (txt, c) in enumerate(boxes):
        ax.add_patch(FancyBboxPatch((x, 0.7), w, h,
                                    boxstyle="round,pad=0.05",
                                    fc=c, ec="#555", lw=1.2))
        ax.text(x + w/2, 1.2, txt, ha="center", va="center", fontsize=9)
        if i < len(boxes) - 1:
            ax.add_patch(FancyArrowPatch((x + w, 1.2), (x + w + gap, 1.2),
                                         arrowstyle="-|>", mutation_scale=14,
                                         color="#333"))
        x += w + gap
    ax.set_xlim(-0.2, x)
    ax.set_ylim(0.3, 2.2)
    plt.tight_layout()
    plt.savefig(os.path.join(RES, "fig1_workflow.png"), dpi=170)
    plt.close()


# ---------------- Fig 2: film stack + TMM ----------------
def fig2():
    fig, ax = plt.subplots(figsize=(4.2, 5))
    ax.axis("off")
    # draw from substrate (bottom) to air (top): Glass, L, H, L, H, Air
    layers = [
        ("Glass  ns=1.52", "#d9d9d9", 0.9),
        ("L  nL=1.45\n d4", "#4f81bd", 0.6),
        ("H  nH=2.30\n d3", "#c0504d", 0.7),
        ("L  nL=1.45\n d2", "#4f81bd", 0.6),
        ("H  nH=2.30\n d1", "#c0504d", 0.7),
        ("Air  n0=1.00", "#f2f2f2", 0.0),
    ]
    y = 0.0
    for label, color, h in layers:
        ax.add_patch(Rectangle((0.3, y), 1.6, h, fc=color, ec="#333"))
        ax.text(1.1, y + h/2, label, ha="center", va="center",
                fontsize=9, color="white" if color not in ("#f2f2f2", "#d9d9d9") else "black")
        y += h
    # incident / reflected arrows
    ax.add_patch(FancyArrowPatch((0.05, y - 0.3), (0.55, y - 0.55),
                                 arrowstyle="-|>", mutation_scale=16, color="red"))
    ax.text(0.0, y - 0.25, "I(λ)", color="red", fontsize=10)
    ax.add_patch(FancyArrowPatch((0.55, y - 0.75), (0.05, y - 1.0),
                                 arrowstyle="-|>", mutation_scale=16, color="blue"))
    ax.text(0.0, y - 1.05, "R(λ)", color="blue", fontsize=10)
    ax.set_xlim(-0.2, 2.3)
    ax.set_ylim(-0.2, y + 0.2)
    ax.set_title("Air / H / L / H / L / Glass", fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(RES, "fig2_stack.png"), dpi=170)
    plt.close()


# ---------------- Fig 3: MLP architecture ----------------
def fig3():
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.axis("off")
    sizes = [4, 128, 128, 64, 41]
    labels = ["input\nd1..d4", "hidden", "hidden", "hidden", "output\nR(λ), 41"]
    xs = [0.0, 1.6, 3.2, 4.8, 6.6]
    # draw neurons as dots, scaled down visually
    for x, s, lab in zip(xs, sizes, labels):
        n_show = min(s, 6)
        ys = [1.0 + (i - (n_show-1)/2)*0.32 for i in range(n_show)]
        for yy in ys:
            ax.plot(x, yy, "o", ms=9, color="#5b9bd5", mec="#2f5f8f")
        if s > 6:
            ax.text(x, 1.0, "· · ·", ha="center", va="center", fontsize=11, color="#2f5f8f")
        ax.text(x, -0.25, lab, ha="center", fontsize=9)
        ax.text(x, 2.6, f"{s}", ha="center", fontsize=9, color="#2f5f8f")
    # connections between adjacent layers (a few)
    for i in range(len(xs)-1):
        for a in [0.0, 0.64, 1.28]:
            for b in [0.0, 0.64, 1.28]:
                ax.plot([xs[i], xs[i+1]], [1.0+a, 1.0+b], color="#bbbbbb", lw=0.5, zorder=0)
    ax.set_xlim(-0.4, 7.2)
    ax.set_ylim(-0.6, 2.9)
    plt.tight_layout()
    plt.savefig(os.path.join(RES, "fig3_mlp.png"), dpi=170)
    plt.close()


if __name__ == "__main__":
    fig1(); fig2(); fig3()
    print("saved fig1/fig2/fig3")
