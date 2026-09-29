"""
tmm.py — Transfer Matrix Method (TMM) for multilayer dielectric thin films.

Stack: Air (n0=1) / H(nH) / L(nL) / H(nH) / L(nL) / Glass substrate (ns)
Normal incidence, no absorption, no dispersion.

Layer order (from incident/air side to substrate side):
    d1 -> H layer (nH)
    d2 -> L layer (nL)
    d3 -> H layer (nH)
    d4 -> L layer (nL)

For layer j with index n_j and physical thickness d_j:
    delta_j = 2*pi*n_j*d_j / lambda
    M_j = [[ cos(delta_j),   i*sin(delta_j)/n_j ],
           [ i*n_j*sin(delta_j),   cos(delta_j)   ]]
    (at normal incidence s and p are degenerate; q_j = n_j)

Total matrix M = M1 M2 M3 M4.
With M = [[m11,m12],[m21,m22]] and substrate admittance eta_s = ns:
    B = m11 + m12*ns
    C = m21 + m22*ns
    r = (n0*B - C) / (n0*B + C),   n0 = 1 (air)
    R = |r|^2
"""
import numpy as np

# ---- fixed optical constants (unified across the class) ----
N0 = 1.0    # incident medium: air
NH = 2.30   # high-index layer
NL = 1.45   # low-index layer
NS = 1.52   # glass substrate

LAMBDAS = np.arange(400.0, 801.0, 10.0)  # 400..800 nm, step 10 nm -> 41 pts


def _layer_matrix(n, d, lam):
    """Return (len(lam),2,2) complex characteristic matrix for one layer."""
    delta = 2.0 * np.pi * n * d / lam
    cosd = np.cos(delta)
    sind = np.sin(delta)
    M = np.zeros((len(lam), 2, 2), dtype=complex)
    M[:, 0, 0] = cosd
    M[:, 0, 1] = 1j * sind / n
    M[:, 1, 0] = 1j * sind * n
    M[:, 1, 1] = cosd
    return M


def reflectance(d1, d2, d3, d4, lam=LAMBDAS):
    """Reflectance R(lambda) for the H/L/H/L stack.

    d1..d4 : layer thicknesses in nm (scalars)
    lam    : wavelength grid in nm (1D array)
    returns R : real array in [0,1], same length as lam
    """
    lam = np.asarray(lam, dtype=float)
    M = (_layer_matrix(NH, d1, lam) @
         _layer_matrix(NL, d2, lam) @
         _layer_matrix(NH, d3, lam) @
         _layer_matrix(NL, d4, lam))
    m11, m12 = M[:, 0, 0], M[:, 0, 1]
    m21, m22 = M[:, 1, 0], M[:, 1, 1]
    B = m11 + m12 * NS
    C = m21 + m22 * NS
    r = (N0 * B - C) / (N0 * B + C)
    return np.abs(r) ** 2


def reflectance_batch(thick, lam=LAMBDAS):
    """Vectorised batch version.

    thick : (N,4) array of thicknesses [d1,d2,d3,d4] in nm
    returns R : (N, len(lam)) array of reflectance
    """
    thick = np.asarray(thick, dtype=float)
    out = np.empty((thick.shape[0], len(lam)), dtype=float)
    for i in range(thick.shape[0]):
        out[i] = reflectance(thick[i, 0], thick[i, 1],
                             thick[i, 2], thick[i, 3], lam)
    return out


if __name__ == "__main__":
    # ---- self checks ----
    # 1) bare glass (zero layers): R = ((ns-1)/(ns+1))^2
    R_bare = reflectance(0.0, 0.0, 0.0, 0.0)
    R_expected = ((NS - N0) / (NS + N0)) ** 2
    print(f"[check1] bare-glass R(mean) = {R_bare.mean():.4f}, "
          f"expected = {R_expected:.4f}")
    assert abs(R_bare.mean() - R_expected) < 1e-9, "bare glass check failed"

    # 2) a quarter-wave-ish stack should give R in [0,1] everywhere
    R = reflectance(90.0, 90.0, 90.0, 90.0)
    print(f"[check2] 90nm stack: R min={R.min():.4f} max={R.max():.4f}, "
          f"R@480nm={R[np.argmin(np.abs(LAMBDAS-480))]:.4f}")
    assert R.min() >= -1e-9 and R.max() <= 1.0 + 1e-9

    # 3) batch == loop
    tb = np.array([[82, 120, 80, 120], [60, 100, 140, 100]], dtype=float)
    rb_loop = np.vstack([reflectance(*row) for row in tb])
    rb_batch = reflectance_batch(tb)
    print(f"[check3] batch-vs-loop max abs diff = {np.abs(rb_loop-rb_batch).max():.2e}")
    assert np.allclose(rb_loop, rb_batch)
    print("All TMM self-checks passed.")
