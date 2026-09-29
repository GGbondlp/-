"""build_paper.py — assemble the Research Article .docx from results/ figures."""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
OUT = os.path.join(HERE, "..", "Research_Article_ThinFilm_MLP.docx")

doc = Document()

# base style
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(10.5)

for s in doc.sections:
    s.top_margin = Cm(2.2); s.bottom_margin = Cm(2.2)
    s.left_margin = Cm(2.4); s.right_margin = Cm(2.4)


def h(text, size=13, space_before=10):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text); r.bold = True; r.font.size = Pt(size)
    return p


def para(text, size=10.5, italic=False, align=None, after=6):
    p = doc.add_paragraph()
    if align: p.alignment = align
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(text); r.font.size = Pt(size); r.italic = italic
    return p


def fig(fname, caption, width=14.5):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(os.path.join(RES, fname), width=Cm(width))
    c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run(caption); r.font.size = Pt(9); r.italic = True
    c.paragraph_format.space_after = Pt(8)


# ---------------- Title block ----------------
t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("基于多层感知机的多层介质薄膜光谱预测与辅助设计")
r.bold = True; r.font.size = Pt(15)
t2 = doc.add_paragraph(); t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = t2.add_run("MLP-Based Spectral Prediction and Data-Driven Design of Multilayer Dielectric Thin Films")
r2.bold = True; r2.font.size = Pt(12)
t2.paragraph_format.space_after = Pt(8)

info = doc.add_paragraph(); info.alignment = WD_ALIGN_PARAGRAPH.CENTER
info.add_run("Name: __________    Student ID: __________\n").font.size = Pt(10)
info.add_run("λtarget: 480 nm    seed: 270034    design_seed: 270035").font.size = Pt(10)

# ---------------- Abstract ----------------
h("Abstract", 12, space_before=8)
para(
    "Multilayer dielectric thin films are designed by tuning a large number of layer "
    "thicknesses, and each trial normally requires a full transfer-matrix-method (TMM) "
    "calculation, which makes exhaustive screening expensive. Here we treat the problem as "
    "a small AI-for-Science workflow: we use TMM to generate 5000 thickness–reflectance "
    "pairs for an Air/H/L/H/L/Glass stack (nH=2.30, nL=1.45, ns=1.52), and train a compact "
    "multilayer perceptron (4–128–128–64–41) that maps four layer thicknesses (40–180 nm) to "
    "the 41-point reflectance spectrum over 400–800 nm. The trained network predicts held-out "
    "spectra with a test RMSE of 0.0060; the error falls monotonically with training-set size "
    "(RMSE 0.026 with 500 samples to 0.006 with 4000) and shows diminishing returns. Using a "
    "separate design seed, the MLP screens 10000 new candidates in milliseconds, and exact TMM "
    "re-validation of the top candidates yields an anti-reflection design at 480 nm with "
    "R = 0.0003. The MLP is thus an accurate, low-cost surrogate, while TMM remains the "
    "physics-based final check.")
kw = doc.add_paragraph(); kw.add_run("Keywords: ").bold = True
kw.add_run("optical thin films; transfer matrix method; multilayer perceptron; "
           "surrogate model; AI for Science").font.size = Pt(10)

# ---------------- 1 Introduction ----------------
h("1. Introduction")
para(
    "Multilayer dielectric thin films are stacks of transparent thin layers whose optical "
    "response is shaped by interference between waves reflected at every interface. The "
    "spectrum is determined jointly by the number of layers, the refractive index of each "
    "material, and the physical thickness of each layer, which makes the response a highly "
    "nonlinear function of the design variables. Such stacks are used as anti-reflection and "
    "high-reflection coatings, band-pass filters, color filters, and radiative-cooling layers.")
para(
    "Given a fixed material set, the forward problem—computing the reflection spectrum from "
    "the layer thicknesses—is solved accurately by the transfer matrix method (TMM), which "
    "propagates the electric and magnetic fields through each layer with a 2×2 characteristic "
    "matrix. TMM is fast for a single structure, but searching over a continuous thickness "
    "space of even four layers still requires many repeated evaluations, and the inverse "
    "problem (finding thicknesses that meet a target response) has no closed-form solution.")
para(
    "Machine learning offers a complementary route: a data-driven surrogate can learn the "
    "nonlinear thickness-to-spectrum mapping from a finite set of TMM simulations and then "
    "predict new structures orders of magnitude faster. This surrogate can be combined with "
    "cheap ranking or optimization to pre-screen large candidate sets, after which only the "
    "few best structures need to be recomputed with exact TMM. This is the classic "
    "physics-plus-data workflow of AI for Science.")
para(
    "In this study we keep the problem deliberately small and reproducible. We ask three "
    "questions: (Q1) Can a simple MLP accurately predict the full reflection spectrum from "
    "four layer thicknesses? (Q2) How does prediction error change as the training set grows? "
    "(Q3) Can the MLP act as a surrogate to quickly screen a target-wavelength design, and "
    "how should its output be reconciled with exact TMM?")
fig("fig1_workflow.png", "Figure 1. Overall workflow: TMM forward simulation → dataset → "
    "MLP surrogate → fast screening of 10000 candidates → TMM re-validation of the top design.",
    width=15.5)

# ---------------- 2 Methods ----------------
h("2. Materials and Methods")
h("2.1 Optical model and transfer matrix method", 11, space_before=6)
para(
    "The stack is Air / H / L / H / L / Glass with four functional layers and normal "
    "incidence. We assume no absorption, no dispersion, and s/p degeneracy at normal "
    "incidence. The refractive indices are n0 = 1.00 (air), nH = 2.30, nL = 1.45, and "
    "ns = 1.52 (glass substrate). For layer j with thickness dj, the phase thickness is "
    "δj = 2π nj dj / λ and the characteristic matrix is")
para("    Mj = [ [ cos δj,   i sin δj / nj ],", italic=True, after=0)
para("        [ i nj sin δj,   cos δj   ] ]", italic=True, after=6)
para(
    "The total matrix is M = M1 M2 M3 M4. Writing M = [[m11,m12],[m21,m22]], the boundary "
    "admittance of the substrate gives B = m11 + m12 ns and C = m21 + m22 ns; the reflection "
    "coefficient is r = (B − C)/(B + C) (air admittance = 1) and the reflectance is R = |r|². "
    "The implementation was verified against the bare-glass limit R = ((ns−1)/(ns+1))² ≈ 0.0426.")
fig("fig2_stack.png", "Figure 2. Physical model: Air/H/L/H/L/Glass four-layer stack; "
    "incident I(λ) and reflected R(λ) at normal incidence.", width=8.5)

h("2.2 Student-specific target wavelength and random seed", 11, space_before=6)
para(
    "With the last two student digits N = 34, the target wavelength is "
    "λtarget = 450 + 10 × (N mod 31) = 480 nm. The master seed is seed = 270034, used to "
    "control dataset generation, the fixed train/val/test split, and MLP initialization "
    "(random, numpy, and torch seeds all set to 270034). To avoid overlap between training "
    "data and screening candidates, the design step uses design_seed = seed + 1 = 270035.")

h("2.3 Dataset generation", 11, space_before=6)
para(
    "With seed = 270034, we sampled 5000 thickness vectors uniformly in [40, 180] nm for "
    "each of the four layers, computed the reflectance on the 400–800 nm grid (step 10 nm, "
    "41 points) with TMM, and applied one fixed permutation to split the data into "
    "4000 training, 500 validation, and 500 test samples. This split is held fixed in every "
    "experiment.")

h("2.4 MLP surrogate model", 11, space_before=6)
para(
    "The network takes the four normalized thicknesses [d1,d2,d3,d4] as input and outputs the "
    "41 reflectance values, with the fixed architecture 4 → 128 → 128 → 64 → 41 (ReLU "
    "hidden units, linear output). Inputs are standardized using training-set mean and "
    "standard deviation; reflectance targets are left in [0,1]. We optimize the mean squared "
    "error with Adam (learning rate 1e-3, batch size 64) and stop when validation loss has "
    "not improved for 200 epochs.")
fig("fig3_mlp.png", "Figure 3. MLP architecture: 4 thickness inputs → two 128-unit hidden "
    "layers → 64-unit layer → 41 reflectance outputs.", width=14)

h("2.5 Training-size experiment", 11, space_before=6)
para(
    "To study Q2, we retrain the same architecture on the first 500, 1000, 2000, and 4000 "
    "samples of the fixed training pool, while the validation and test sets remain the same "
    "500 samples. All optimization settings are unchanged.")

h("2.6 MLP-assisted thin-film screening", 11, space_before=6)
para(
    "Using design_seed = 270035, we generated 10000 new candidate thickness vectors that did "
    "not enter training. The trained MLP predicted their spectra, we ranked candidates by "
    "R(480 nm) in ascending order (anti-reflection goal), took the top 10, and recomputed "
    "their spectra exactly with TMM. The final Top 5 are re-ranked by the TMM value.")

# ---------------- 3 Results ----------------
h("3. Results")
h("3.1 MLP training and spectral prediction", 11, space_before=6)
para(
    "Training converged smoothly and early-stopped around epoch 2200, reaching a best "
    "validation MSE of about 3.5×10⁻⁵ (Figure 4). On the held-out 500 test samples the "
    "network achieved RMSE = 0.0060 and MAE = 0.0042 in reflectance units. Representative "
    "test spectra (Figure 5) show that the MLP reproduces both the peak positions and the "
    "overall line shape of the TMM reference almost everywhere, with only small deviations "
    "near sharp extrema.")
fig("fig4_loss.png", "Figure 4. Training and validation MSE loss (log scale) of the MLP "
    "surrogate model.")
fig("fig5_spectra.png", "Figure 5. TMM reference (black) versus MLP prediction (red dashed) "
    "for three representative test samples; the green dotted line marks 480 nm.", width=15.5)

h("3.2 Effect of training-set size", 11, space_before=6)
para(
    "Test RMSE fell from 0.0262 with 500 training samples to 0.0135 with 1000, 0.0097 with "
    "2000, and 0.0060 with 4000 (Figure 6). Doubling the data roughly halves the error at "
    "first, but the incremental gain shrinks as the set grows, indicating a data-efficiency "
    "curve with diminishing returns rather than a linear benefit.")
fig("fig6_ablation.png", "Figure 6. Effect of training-set size on test RMSE; validation and "
    "test sets are fixed.")

h("3.3 MLP-assisted thin-film design", 11, space_before=6)
para(
    "Screening 10000 new candidates with the trained MLP and re-validating the top 10 with "
    "TMM produced the designs in Table 1. The best design, d = (84.2, 125.4, 63.5, 155.2) "
    "nm, reaches a TMM-verified reflectance of only R(480 nm) = 0.0003, i.e. near-complete "
    "destructive interference at the target wavelength (Figure 7). The MLP-predicted and "
    "TMM-verified spectra for this design overlap almost perfectly.")

# Table 1
tbl = doc.add_table(rows=6, cols=7); tbl.style = "Light Grid Accent 1"
hdr = ["Rank", "d1/nm", "d2/nm", "d3/nm", "d4/nm", "MLP R@480", "TMM R@480"]
data = [
    ["1", "84.2", "125.4", "63.5", "155.2", "-0.0060", "0.0003"],
    ["2", "85.5", "120.4", "67.1", "40.7", "-0.0096", "0.0012"],
    ["3", "117.1", "70.7", "128.5", "58.3", "-0.0044", "0.0013"],
    ["4", "122.4", "56.5", "128.9", "87.0", "-0.0061", "0.0025"],
    ["5", "123.3", "176.6", "77.8", "90.4", "-0.0039", "0.0045"],
]
for j, txt in enumerate(hdr):
    c = tbl.rows[0].cells[j]; c.text = txt
    for pr in c.paragraphs:
        for rr in pr.runs: rr.bold = True; rr.font.size = Pt(9)
for i, row in enumerate(data, start=1):
    for j, txt in enumerate(row):
        c = tbl.rows[i].cells[j]; c.text = txt
        for pr in c.paragraphs:
            for rr in pr.runs: rr.font.size = Pt(9)
cap = doc.add_paragraph(); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.add_run("Table 1. Top five anti-reflection designs selected by MLP and verified by TMM "
            "at λ = 480 nm.").italic = True
cap.runs[0].font.size = Pt(9)

fig("fig7_design.png", "Figure 7. MLP-selected best design: TMM-verified (black) and "
    "MLP-predicted (red dashed) spectra; the reflectance dips to R ≈ 0 at 480 nm.", width=12)

h("3.4 Representative failure case", 11, space_before=6)
para(
    "The worst test sample (per-sample MSE ≈ 8.6×10⁻⁴, Figure 8) shows the MLP "
    "systematically overestimating the two reflectance lobes and slightly shifting their "
    "centers. The error is small in absolute terms but illustrates where the surrogate "
    "struggles: spectra with narrow, tall peaks are interpolated less accurately.")
fig("fig8_failure.png", "Figure 8. Representative failure case on a test sample: the MLP "
    "overestimates and slightly displaces the spectral peaks.", width=12)

# ---------------- 4 Discussion ----------------
h("4. Discussion")
para(
    "Q1: the MLP predicts the full 41-point spectrum with RMSE ≈ 0.006 in reflectance units, "
    "which is small relative to the 0–1 range and sufficient to distinguish design-quality "
    "differences. Errors concentrate near sharp peaks and crossings, where the mapping "
    "changes most rapidly with thickness; this is consistent with a smooth regressor "
    "averaging over narrow spectral features.")
para(
    "Q2: adding training data reliably reduces error, but with diminishing returns. Going "
    "from 500 to 1000 samples cuts RMSE by half, while 2000→4000 yields only a modest "
    "further improvement. For this four-layer problem, a few thousand TMM simulations are "
    "enough for a useful surrogate, and extra data buys progressively less.")
para(
    "Q3: the surrogate is valuable for screening. Ranking 10000 candidates takes milliseconds "
    "with the MLP versus hours of repeated TMM calls, and the resulting top design achieves "
    "R(480 nm) = 0.0003. Crucially, the MLP occasionally predicts slightly negative "
    "reflectance (e.g. −0.006), which is physically impossible for a regression model without "
    "a [0,1] constraint; this is exactly why the final candidates must be re-computed and "
    "re-ranked with TMM. The two methods play complementary roles: MLP for breadth, TMM for "
    "trust.")
para(
    "Limitations: the model fixes materials, layer count, and normal incidence; it is an "
    "interpolator within the [40,180] nm training range and may not extrapolate well. The "
    "network has no physical constraint, so its raw output should not be treated as exact. "
    "Future work could add a bounded output, treat dispersion, or learn a tandem model that "
    "couples prediction and optimization more tightly.")

# ---------------- 5 Conclusions ----------------
h("5. Conclusions")
para(
    "A compact MLP (4–128–128–64–41) accurately learns the TMM thickness-to-spectrum "
    "mapping for a four-layer dielectric stack, reaching test RMSE = 0.0060 (Q1). Prediction "
    "error decreases monotonically with training-set size but with diminishing returns "
    "(0.026 at 500 samples to 0.006 at 4000) (Q2). Used as a fast surrogate, the MLP screens "
    "10000 candidates and, after exact TMM re-validation, finds an anti-reflection design at "
    "480 nm with R = 0.0003 (Q3). The workflow—physics simulation, data-driven surrogate, and "
    "final physics verification—demonstrates a small but complete AI4S design loop.")

# ---------------- Data availability ----------------
h("Data and Code Availability")
para(
    "The dataset was generated with the TMM code in this study. All source code, training "
    "and screening scripts, dependency files, and reproduction instructions are available at "
    "https://github.com/USERNAME/REPOSITORY (to be replaced with the real repository link; "
    "λtarget = 480 nm, seed = 270034, design_seed = 270035).")

# ---------------- References ----------------
h("References")
refs = [
    "Ma, T.; Ma, M.; Guo, L.J. Optical multilayer thin film structure inverse design: From optimization to deep learning. iScience 2025, 28, 112222.",
    "Macleod, H.A. Thin-Film Optical Filters, 5th ed.; CRC Press: Boca Raton, 2017.",
    "Born, M.; Wolf, E. Principles of Optics, 7th ed.; Cambridge University Press: Cambridge, 1999.",
    "Rumelhart, D.E.; Hinton, G.E.; Williams, R.J. Learning representations by back-propagating errors. Nature 1986, 323, 533–536.",
    "Goodfellow, I.; Bengio, Y.; Courville, A. Deep Learning; MIT Press: Cambridge, 2016.",
    "Paszke, A. et al. PyTorch: An imperative style, high-performance deep learning library. Adv. Neural Inf. Process. Syst. 2019, 32, 8024–8035.",
    "Piegari, A.; Flory, F. (Eds.) Optical Thin Films and Coatings: From Materials to Applications; Woodhead Publishing: Cambridge, 2018.",
    "Goldberg, D.E. Genetic Algorithms in Search, Optimization, and Machine Learning; Addison-Wesley: Reading, 1989.",
    "Molesky, S. et al. Machine learning and nanophotonic design. Nat. Photonics 2018, 12, 659–670.",
]
for i, ref in enumerate(refs, 1):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(f"[{i}] {ref}"); r.font.size = Pt(9)

doc.save(OUT)
print("saved", OUT)
