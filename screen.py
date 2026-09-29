"""
screen.py — MLP-assisted thin-film screening + TMM verification.

Uses design_seed = seed+1 = 270035 to generate 10000 NEW candidate stacks,
predicts their spectra with the trained MLP, sorts by R(lambda=480 nm)
ASCENDING (anti-reflection goal), takes Top 10, recomputes with TMM,
and reports the final Top 5.

Outputs:
  results/table1_top5.csv
  results/fig7_design.png
  results/screen_candidates.npz
"""
import os, sys
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from model import MLP
from tmm import reflectance, LAMBDAS

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")

SEED = 270034
DESIGN_SEED = SEED + 1          # 270035
LAM_TGT = 480.0
N_CAND = 10000
D_MIN, D_MAX = 40.0, 180.0


def main():
    # ---- load trained MLP ----
    ckpt = torch.load(os.path.join(RES, "mlp_main.pt"), map_location="cpu",
                      weights_only=False)
    model = MLP()
    model.load_state_dict(ckpt["state"])
    model.eval()
    mu, sd = ckpt["mu"], ckpt["sd"]

    # ---- generate 10000 new candidates with design_seed ----
    rng = np.random.default_rng(DESIGN_SEED)
    cand = rng.uniform(D_MIN, D_MAX, size=(N_CAND, 4)).astype(np.float32)

    # ---- MLP predict ----
    x = torch.tensor((cand - mu) / sd, dtype=torch.float32)
    with torch.no_grad():
        pred = model(x).numpy()
    idx480 = int(np.argmin(np.abs(LAMBDAS - LAM_TGT)))
    mlp_rtgt = pred[:, idx480]

    # ---- sort ascending (minimize R at target) ----
    order = np.argsort(mlp_rtgt)
    top10 = order[:10]

    # ---- TMM re-verify Top 10 ----
    rows = []
    for k in top10:
        d = cand[k]
        tmm_spec = reflectance(d[0], d[1], d[2], d[3], LAMBDAS)
        rows.append(dict(
            d1=float(d[0]), d2=float(d[1]), d3=float(d[2]), d4=float(d[3]),
            mlp_rtgt=float(mlp_rtgt[k]),
            tmm_rtgt=float(tmm_spec[idx480]),
        ))

    # re-sort the Top10 by TMM-verified target reflectance, keep best 5
    rows.sort(key=lambda r: r["tmm_rtgt"])
    top5 = rows[:5]

    # ---- write Table 1 ----
    with open(os.path.join(RES, "table1_top5.csv"), "w") as f:
        f.write("Rank,d1/nm,d2/nm,d3/nm,d4/nm,MLP_R@480,TMM_R@480\n")
        for i, r in enumerate(top5, 1):
            f.write(f"{i},{r['d1']:.1f},{r['d2']:.1f},{r['d3']:.1f},{r['d4']:.1f},"
                    f"{r['mlp_rtgt']:.4f},{r['tmm_rtgt']:.4f}\n")
    print("== Top 5 designs (TMM-verified) ==")
    for i, r in enumerate(top5, 1):
        print(f"  #{i}: d=({r['d1']:.0f},{r['d2']:.0f},{r['d3']:.0f},{r['d4']:.0f}) nm  "
              f"MLP R@480={r['mlp_rtgt']:.4f}  TMM R@480={r['tmm_rtgt']:.4f}")

    # ---- Fig 7: best design, MLP vs TMM ----
    best = top5[0]
    tmm_best = reflectance(best["d1"], best["d2"], best["d3"], best["d4"], LAMBDAS)
    mlp_best_pred = model(torch.tensor(
        (np.array([best['d1'],best['d2'],best['d3'],best['d4']],dtype=np.float32)-mu)/sd,
        dtype=torch.float32)).detach().numpy().ravel()

    plt.figure(figsize=(6, 3.8))
    plt.plot(LAMBDAS, tmm_best, "k-", lw=1.9, label="TMM (verified)")
    plt.plot(LAMBDAS, mlp_best_pred, "r--", lw=1.6, label="MLP (surrogate)")
    plt.axvline(480, color="g", ls=":", lw=1.2)
    plt.scatter([480], [best["tmm_rtgt"]], color="g", zorder=5)
    plt.annotate(f"  R(480nm)={best['tmm_rtgt']:.3f}", (480, best["tmm_rtgt"]),
                 fontsize=9, color="g")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Reflectance R")
    plt.title("MLP-selected best anti-reflection design (TMM-verified)")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(RES, "fig7_design.png"), dpi=160)
    plt.close()

    np.savez(os.path.join(RES, "screen_candidates.npz"),
             cand=cand, mlp_rtgt=mlp_rtgt)
    print("Saved table1_top5.csv, fig7_design.png")


if __name__ == "__main__":
    main()
