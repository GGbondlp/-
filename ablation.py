"""
ablation.py — effect of training-set size on test error.

Trains the same MLP on the first 500 / 1000 / 2000 / 4000 samples of the
fixed training pool; validation and test sets are always the fixed 500 samples.
All other training settings identical.

Outputs:
  results/fig6_ablation.png
  results/ablation_metrics.txt
"""
import os, sys
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from train import train_mlp

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")

SIZES = [500, 1000, 2000, 4000]


def main():
    rows = []
    for n in SIZES:
        print(f"== ablation: n_train={n} ==")
        model, tensors, hist, d = train_mlp(n_train=n, verbose=False)
        model.eval()
        with torch.no_grad():
            pred = model(tensors["x_te"]).numpy()
        true = tensors["y_te"].numpy()
        rmse = float(np.sqrt(np.mean((pred - true) ** 2)))
        mae = float(np.mean(np.abs(pred - true)))
        rows.append((n, rmse, mae))
        print(f"   test RMSE={rmse:.5f}  MAE={mae:.5f}")

    ns = [r[0] for r in rows]
    rmses = [r[1] for r in rows]

    with open(os.path.join(RES, "ablation_metrics.txt"), "w") as f:
        f.write("n_train,RMSE,MAE\n")
        for n, rm, ma in rows:
            f.write(f"{n},{rm:.5f},{ma:.5f}\n")

    plt.figure(figsize=(5.2, 3.6))
    plt.plot(ns, rmses, "o-", color="#1f77b4", lw=1.8, ms=7)
    for n, rm in zip(ns, rmses):
        plt.annotate(f"{rm:.4f}", (n, rm), textcoords="offset points",
                     xytext=(0, 8), ha="center", fontsize=8)
    plt.xlabel("Number of training samples")
    plt.ylabel("Test RMSE")
    plt.title("Effect of training-set size on prediction error")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(RES, "fig6_ablation.png"), dpi=160)
    plt.close()
    print("Saved fig6_ablation.png and ablation_metrics.txt")


if __name__ == "__main__":
    main()
