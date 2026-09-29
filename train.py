"""
train.py — train the MLP surrogate model and produce main results.

Run:  python src/train.py
Outputs (in results/):
  mlp_main.pt            trained model weights + normalizer stats
  loss_history.npz       train/val loss per epoch
  fig4_loss.png          training/validation loss curves
  fig5_spectra.png       TMM vs MLP on 3 representative test samples
  fig8_failure.png        worst test-sample prediction (failure case)
  test_metrics.txt        test RMSE / MAE
"""
import os, sys
import numpy as np
import torch
import torch.nn as nn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from model import MLP
from common import load_dataset, to_tensors

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
os.makedirs(RES, exist_ok=True)

SEED = 270034
EPOCHS = 3000
BATCH = 64
LR = 1e-3
PATIENCE = 200


def train_mlp(n_train=None, seed=SEED, verbose=True):
    torch.manual_seed(seed)
    np.random.seed(seed)
    d = load_dataset()
    tensors = to_tensors(d, n_train=n_train)

    model = MLP(in_dim=4, hidden=(128, 128, 64), out_dim=41)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    lossf = nn.MSELoss()

    x_tr, y_tr = tensors["x_tr"], tensors["y_tr"]
    x_va, y_va = tensors["x_va"], tensors["y_va"]
    n = x_tr.shape[0]

    hist_tr, hist_va = [], []
    best_va, best_state, bad = np.inf, None, 0
    for ep in range(EPOCHS):
        model.train()
        perm = torch.randperm(n)
        ep_loss = 0.0
        for i in range(0, n, BATCH):
            idx = perm[i:i + BATCH]
            opt.zero_grad()
            pred = model(x_tr[idx])
            loss = lossf(pred, y_tr[idx])
            loss.backward()
            opt.step()
            ep_loss += loss.item() * len(idx)
        ep_loss /= n

        model.eval()
        with torch.no_grad():
            va_loss = lossf(model(x_va), y_va).item()
        hist_tr.append(ep_loss)
        hist_va.append(va_loss)

        if va_loss < best_va:
            best_va = va_loss
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            bad = 0
        else:
            bad += 1
        if verbose and (ep % 100 == 0 or ep == EPOCHS - 1):
            print(f"  epoch {ep:4d}  train {ep_loss:.3e}  val {va_loss:.3e}  best {best_va:.3e}")
        if bad >= PATIENCE:
            if verbose:
                print(f"  early stop at epoch {ep} (best val {best_va:.3e})")
            break

    model.load_state_dict(best_state)
    return model, tensors, dict(train=hist_tr, val=hist_va), d


def main():
    print("== Training main MLP (n_train=4000) ==")
    model, tensors, hist, d = train_mlp(n_train=4000)

    # save model + normalizer
    norm = tensors["norm"]
    torch.save(dict(
        state=model.state_dict(),
        mu=norm.mu, sd=norm.sd,
        seed=SEED,
    ), os.path.join(RES, "mlp_main.pt"))
    np.savez(os.path.join(RES, "loss_history.npz"),
             train=hist["train"], val=hist["val"])

    # ---- Fig 4: loss curves ----
    plt.figure(figsize=(5, 3.6))
    plt.plot(hist["train"], label="Train", lw=1.2)
    plt.plot(hist["val"], label="Validation", lw=1.2)
    plt.yscale("log")
    plt.xlabel("Epoch")
    plt.ylabel("MSE loss (log)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RES, "fig4_loss.png"), dpi=160)
    plt.close()

    # ---- test evaluation ----
    model.eval()
    with torch.no_grad():
        pred_te = model(tensors["x_te"]).numpy()
    true_te = tensors["y_te"].numpy()
    rmse = float(np.sqrt(np.mean((pred_te - true_te) ** 2)))
    mae = float(np.mean(np.abs(pred_te - true_te)))
    with open(os.path.join(RES, "test_metrics.txt"), "w") as f:
        f.write(f"test RMSE = {rmse:.5f}\n")
        f.write(f"test MAE  = {mae:.5f}\n")
        f.write(f"n_train   = 4000\n")
    print(f"== Test RMSE={rmse:.5f}  MAE={mae:.5f} ==")

    lam = d["lambdas"]

    # ---- Fig 5: 3 representative test samples ----
    # pick one low-error, one mid, one high-error representative
    err_per_sample = np.mean((pred_te - true_te) ** 2, axis=1)
    order = np.argsort(err_per_sample)
    picks = [order[len(order) // 10], order[len(order) // 2], order[int(len(order)*0.9)]]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.2), sharey=True)
    for ax, k in zip(axes, picks):
        ax.plot(lam, true_te[k], "k-", lw=1.8, label="TMM")
        ax.plot(lam, pred_te[k], "r--", lw=1.6, label="MLP")
        ax.set_title(f"test sample #{k}  MSE={err_per_sample[k]:.2e}", fontsize=9)
        ax.set_xlabel("Wavelength (nm)")
        ax.axvline(480, color="g", ls=":", lw=1)
    axes[0].set_ylabel("Reflectance R")
    axes[0].legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(RES, "fig5_spectra.png"), dpi=160)
    plt.close()

    # ---- Fig 8: failure case = worst test sample ----
    worst = int(np.argmax(err_per_sample))
    plt.figure(figsize=(5.5, 3.6))
    plt.plot(lam, true_te[worst], "k-", lw=1.8, label="TMM")
    plt.plot(lam, pred_te[worst], "r--", lw=1.6, label="MLP")
    plt.axvline(480, color="g", ls=":", lw=1, label=r"$\lambda_{target}=480$ nm")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Reflectance R")
    plt.title(f"Failure case: test sample #{worst}, MSE={err_per_sample[worst]:.2e}")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(RES, "fig8_failure.png"), dpi=160)
    plt.close()
    print("Saved fig4/fig5/fig8 and test_metrics.txt")


if __name__ == "__main__":
    main()
