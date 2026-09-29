# TMM-AI4S: MLP-Based Spectral Prediction and Data-Driven Design of Multilayer Dielectric Thin Films

AI4S course project — thin film technology.
We use the **Transfer Matrix Method (TMM)** to generate *thickness → reflection spectrum* data,
train a small **MLP surrogate model** to approximate TMM, and use the MLP to rapidly screen
anti-reflection designs at a personalized target wavelength; the final candidates are
re-validated with exact TMM.

## Personalized parameters (derived from student ID)

| Parameter | Value | How it is obtained |
|---|---|---|
| `seed` | **270034** | last 6 digits of student ID |
| target wavelength `λ_target` | **480 nm** | `450 + 10 × (N mod 31)`, N = last 2 digits = 34 → `450 + 10×3 = 480` |
| `design_seed` | **270035** | `seed + 1` (used only when screening new candidates) |

Randomness control: `random.seed(seed)`, `np.random.seed(seed)`, `torch.manual_seed(seed)`.

## Physical model (unified settings)

- Stack: **Air / H / L / H / L / Glass**, 4 layers.
- Refractive indices: `n0 = 1.00` (air), `nH = 2.30`, `nL = 1.45`, `ns = 1.52` (glass);
  no absorption, no dispersion, normal incidence.
- Each layer thickness `d1..d4` sampled uniformly in **[40, 180] nm**.
- Wavelength grid: **400–800 nm, step 10 nm → 41 points**.
- 5000 samples, fixed split **4000 / 500 / 500** (train / validation / test).
- MLP: **4 → 128 → 128 → 64 → 41**, MSE loss, Adam.

## Repository structure

```
TMM-AI4S/
├── README.md
├── requirements.txt
├── data/
│   └── dataset.npz          # generated 5000-sample dataset
├── src/
│   ├── tmm.py               # transfer-matrix forward model (+ self-checks)
│   ├── generate_data.py     # seed-controlled data generation & split
│   ├── common.py            # data loading / normalization
│   ├── model.py             # MLP definition
│   ├── train.py             # train main model; Figs.4,5,8; test metrics
│   ├── ablation.py          # training-size experiment (Fig.6)
│   ├── screen.py            # design_seed screening + TMM verify (Fig.7, Table 1)
│   └── make_schemas.py      # schematic Figs.1,2,3
└── results/                 # all figures, tables, model weights
```

## Environment setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# (CPU-only torch is enough; e.g. pip install torch --index-url https://download.pytorch.org/whl/cpu)
```

## Reproduce all results

```bash
source .venv/bin/activate
python src/tmm.py            # sanity check: bare-glass R ≈ 0.0426
python src/generate_data.py  # rebuild data/dataset.npz with seed=270034
python src/train.py          # main model, Figs.4/5/8, test RMSE
python src/ablation.py       # Fig.6 (500/1000/2000/4000)
python src/screen.py         # Fig.7 + Table 1 Top-5
python src/make_schemas.py   # Figs.1/2/3
```

## Key results

- Main model test error: **RMSE = 0.0060**, MAE = 0.0042 (reflectance in [0,1]).
- Training-size effect: RMSE 0.0262 (500) → 0.0135 (1000) → 0.0097 (2000) → 0.0060 (4000).
- Best anti-reflection design at λ=480 nm: **d = (84.2, 125.4, 63.5, 155.2) nm**,
  TMM-verified **R(480 nm) = 0.0003** (near-zero reflectance).

## Notes

- The MLP is a surrogate: it can output slightly negative R (regression without physical
  bounds); the final Top-5 are always re-computed and re-ranked with exact TMM.
