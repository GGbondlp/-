"""common.py — shared data loading / normalization helpers."""
import os
import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "dataset.npz")


def load_dataset():
    d = np.load(DATA)
    return dict(
        thick=d["thick"].astype(np.float32),
        spec=d["spec"].astype(np.float32),
        lambdas=d["lambdas"].astype(np.float32),
        train_idx=d["train_idx"],
        val_idx=d["val_idx"],
        test_idx=d["test_idx"],
        seed=int(d["seed"]),
    )


class InputNorm:
    """Standardize thickness inputs using train-set statistics."""
    def __init__(self, x_train):
        self.mu = x_train.mean(axis=0, keepdims=True)
        self.sd = x_train.std(axis=0, keepdims=True) + 1e-8

    def __call__(self, x):
        return (x - self.mu) / self.sd


def to_tensors(d, n_train=None, device="cpu"):
    """Build normalized train/val/test tensors.

    n_train: if given, use only the first n_train samples of the train pool
             (used by the training-size ablation).
    """
    thick, spec = d["thick"], d["spec"]
    tr, va, te = d["train_idx"], d["val_idx"], d["test_idx"]
    if n_train is not None:
        tr = tr[:n_train]

    norm = InputNorm(thick[tr])
    def T(x):
        return torch.tensor(norm(x), dtype=torch.float32, device=device)
    def Y(x):
        return torch.tensor(x, dtype=torch.float32, device=device)

    return {
        "x_tr": T(thick[tr]), "y_tr": Y(spec[tr]),
        "x_va": T(thick[va]), "y_va": Y(spec[va]),
        "x_te": T(thick[te]), "y_te": Y(spec[te]),
        "norm": norm,
        "tr_idx": tr, "va_idx": va, "te_idx": te,
    }
