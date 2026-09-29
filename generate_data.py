"""
generate_data.py — generate the 5000-sample thickness<->spectrum dataset.

Personalized parameters (student ID = ...270034):
    seed        = 270034
    lambda_tgt  = 480 nm   (= 450 + 10*(34 mod 31))
    design_seed = seed + 1 = 270035   (used later for screening, NOT here)

Procedure:
  1) seed python/numpy/torch RNGs with `seed`.
  2) sample 5000 thickness vectors d in [40,180] nm (uniform, 4 layers).
  3) label each with TMM reflectance on the 400-800 nm / 10 nm grid (41 pts).
  4) one fixed permutation -> split 4000 / 500 / 500 (train/val/test).
Saves data/dataset.npz.
"""
import numpy as np
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
import torch
from tmm import reflectance_batch, LAMBDAS

SEED = 270034
N = 5000
D_MIN, D_MAX = 40.0, 180.0
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


def main():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)

    # 1) sample thicknesses
    rng = np.random.default_rng(SEED)
    thick = rng.uniform(D_MIN, D_MAX, size=(N, 4))

    # 2) TMM labels
    spec = reflectance_batch(thick, LAMBDAS)  # (N,41)

    # 3) fixed permutation and split
    idx = rng.permutation(N)
    n_tr, n_va = 4000, 500
    tr = idx[:n_tr]
    va = idx[n_tr:n_tr + n_va]
    te = idx[n_tr + n_va:]

    os.makedirs(DATA, exist_ok=True)
    out = os.path.join(DATA, "dataset.npz")
    np.savez(
        out,
        thick=thick.astype(np.float32),
        spec=spec.astype(np.float32),
        lambdas=LAMBDAS.astype(np.float32),
        train_idx=tr.astype(np.int64),
        val_idx=va.astype(np.int64),
        test_idx=te.astype(np.int64),
        seed=np.int64(SEED),
    )
    print(f"saved {out}")
    print(f"thick {thick.shape}, spec {spec.shape}")
    print(f"split sizes: train={len(tr)} val={len(va)} test={len(te)}")
    print(f"thick range: [{thick.min():.1f}, {thick.max():.1f}] nm")
    print(f"spec range:  [{spec.min():.3f}, {spec.max():.3f}]")


if __name__ == "__main__":
    main()
