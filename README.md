# MD-POST

### Automated Multi-System GROMACS Molecular Dynamics Post-Processing, Statistical Analysis & AI-Assisted Interpretation

[![GROMACS](https://img.shields.io/badge/GROMACS-2026.x-blue)](https://www.gromacs.org/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![R](https://img.shields.io/badge/R-4.x-276DC3)](https://www.r-project.org/)
[![MDAnalysis](https://img.shields.io/badge/MDAnalysis-supported-orange)](https://www.mdanalysis.org/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-black)](https://ollama.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**MD-POST** is a modular research-software pipeline for automated post-processing of **GROMACS molecular dynamics simulations**. It is designed for multi-system studies in which the same analysis workflow must be applied consistently across apo, ligand-bound, mutant, control, or other simulation conditions.

The pipeline connects trajectory preprocessing, conventional MD metrics, collective-motion analysis, statistical comparison, figure generation, numerical reporting, and optional local-LLM interpretation into one reproducible workflow.

> **Research software, not an automated scientific decision-maker.** MD-POST automates calculations and reporting. Biological interpretation and final scientific conclusions remain the responsibility of the researcher.

---

## Why MD-POST?

MD analysis often becomes a repetitive sequence of manually executed commands, exported files, plotting scripts, and interpretation steps. That approach makes multi-system studies harder to reproduce and easier to perform inconsistently.

MD-POST addresses this by providing a single pipeline that can:

- discover simulation systems automatically;
- preprocess trajectories consistently;
- calculate standard structural and dynamical descriptors;
- perform advanced collective-motion analyses;
- compare multiple systems statistically;
- generate publication-oriented figures;
- produce machine-readable numerical reports;
- optionally use a **local** LLM for structured interpretation; and
- generate a draft Methods / Results & Discussion document.

---

## Workflow

```text
                         MD-POST WORKFLOW

   GROMACS simulation files
          │
          ▼
┌──────────────────────────────┐
│  01  Trajectory preprocessing│
│  PBC → centering → fitting   │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│  02  Basic MD analysis       │
│  RMSD · RMSF · Rg · SASA     │
│  H-bonds                     │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│  03  Advanced analysis       │
│  PCA · FEL · DSSP · DCCM     │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│  04  Statistical comparison  │
│  Kruskal–Wallis H-test       │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│  05  Visualization            │
│  Individual + overlay plots  │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│  06  Numerical report         │
│  Machine-readable summaries  │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│  07  Local LLM interpretation│
│  Ollama / user-selected model│
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│  08  Manuscript draft         │
│  Markdown · TXT · LaTeX      │
└──────────────────────────────┘
```

---

## Core capabilities

| Module | Capability |
|---|---|
| **Multi-system input** | Automatically discovers system directories under `input/` |
| **Trajectory preprocessing** | PBC no-jump correction, molecular centering, rotational/translational fitting |
| **RMSD** | Backbone structural deviation over time |
| **RMSF** | Residue-level flexibility |
| **Radius of gyration** | Global compactness over time |
| **SASA** | Solvent-accessible surface area |
| **Hydrogen bonds** | Intra-protein H-bond analysis |
| **PCA** | Dominant collective motions and conformational space |
| **FEL** | PC1/PC2 free-energy landscape by Boltzmann inversion |
| **DSSP** | Secondary-structure assignment and temporal visualization |
| **DCCM** | Residue-residue correlated and anti-correlated motions |
| **Statistics** | Kruskal–Wallis non-parametric comparison across systems |
| **Visualization** | Individual plots, cross-system overlays and advanced heatmaps |
| **Numerical reporting** | Consolidated machine-readable summary of calculated metrics |
| **Local LLM** | Optional interpretation using Ollama without sending results to a hosted API |
| **Manuscript builder** | Generates draft Methods and Results & Discussion text in Markdown, TXT and LaTeX |
| **Mock-data validation** | Exercises downstream analysis without requiring trajectory files |

---

## Repository structure

```text
MD-POST/
├── config/
│   └── pipeline_config.sh          # Analysis groups, temperature and Ollama settings
│
├── input/                          # Simulation systems supplied by the user
│   └── SYSTEM_NAME/
│       ├── *.tpr
│       ├── *.xtc
│       └── *.ndx                   # Optional custom index file
│
├── outputs/                        # Generated analysis data
├── figures/                        # Generated figures
│
├── scripts/
│   ├── 01_preprocess.sh            # PBC correction, centering and fitting
│   ├── 02_basic_analysis.sh        # RMSD, RMSF, Rg, SASA and H-bonds
│   ├── 03_advanced_analysis.sh     # PCA, DSSP and DCCM preparation
│   ├── 04_statistics.R             # Kruskal–Wallis statistics
│   ├── 05_plots.py                 # Figure generation
│   ├── 06_llm_interpretation.py    # Local LLM interpretation
│   ├── 07_paper_builder.py         # Manuscript draft generation
│   ├── calculate_dccm.py           # MDAnalysis DCCM calculator
│   ├── generate_mock_data.py       # Synthetic downstream-test dataset
│   └── report_generator.py          # Numerical report generator
│
├── ollama/                         # Local Ollama-related workspace
├── environment.yml                 # Conda environment specification
├── run_pipeline.sh                 # Main pipeline entry point
├── clean_workspace.sh              # Remove generated outputs/figures
└── LICENSE
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/nalgirkarh-prog/MD-POST_PROCESSING_UNIT-MPU-.git
cd MD-POST_PROCESSING_UNIT-MPU-
```

### 2. Create the Conda environment

```bash
conda env create -f environment.yml
conda activate md_pipeline
```

The environment specification includes GROMACS, Python scientific-analysis libraries, MDAnalysis, MDTraj, PyMOL, R and the packages required by the pipeline.

### 3. Optional: install Ollama

LLM functionality is optional. If you want local interpretation and manuscript generation, install Ollama and pull a model:

```bash
ollama pull llama3.2
```

Other lightweight models can be selected through `OLLAMA_MODEL`.

---

## Input format

Place each simulation condition in its own directory under `input/`.

```text
input/
├── APO/
│   ├── system.tpr
│   └── production.xtc
│
├── COMPLEX/
│   ├── system.tpr
│   ├── production.xtc
│   └── index.ndx
│
└── MUTANT/
    ├── system.tpr
    └── production.xtc
```

The pipeline discovers `.tpr`, `.xtc`, `.gro`, `.top` and `.ndx` files by extension rather than requiring a fixed filename.

For a standard run, each system should provide one usable `.tpr` and one trajectory `.xtc`. An `.ndx` file is optional when the default GROMACS groups are sufficient.

---

## Configuration

Edit:

```text
config/pipeline_config.sh
```

Important parameters include:

```bash
GMX_GROUP_RMSD="4"
GMX_GROUP_RMSF="4"
GMX_GROUP_GYRATE="1"
GMX_GROUP_SASA="1"
GMX_GROUP_HBOND_A="1"
GMX_GROUP_HBOND_B="1"
GMX_GROUP_PCA="3"
GMX_GROUP_FIT="4"
SIM_TEMP=300
```

The configured groups correspond to the default GROMACS selection layout expected by the scripts. **If your topology/index contains a different group ordering, update these values before running the pipeline.**

The FEL calculation uses `SIM_TEMP` as its simulation temperature.

Ollama can be configured with:

```bash
export OLLAMA_MODEL="llama3.2"
export OLLAMA_HOST="http://127.0.0.1:11434"
```

---

## Running the pipeline

### Full trajectory workflow

After placing the simulation systems under `input/`:

```bash
bash run_pipeline.sh
```

The launcher will detect the available systems and execute preprocessing and analysis for each system before performing comparative statistics, plotting, report generation and optional LLM interpretation.

### Generate manuscript drafts

After the analysis and interpretation stages complete:

```bash
python scripts/07_paper_builder.py
```

Generated drafts are written to:

```text
outputs/paper/
├── paper_draft.md
├── paper_draft.txt
└── paper_draft.tex
```

### Clean generated results

```bash
bash clean_workspace.sh
```

This removes generated output/figure data while preserving the repository structure.

---

## Mock-data mode

MD-POST includes a synthetic dataset generator for testing the downstream workflow without trajectory files.

```bash
python scripts/generate_mock_data.py
bash run_pipeline.sh
```

The generator creates synthetic outputs for systems such as `APO` and `COMPLEX`, including RMSD, RMSF, Rg, SASA, H-bonds, PCA projections, DSSP data and DCCM matrices.

This mode is intended for **software testing and demonstration**, not scientific validation of a biological hypothesis.

---

## Analysis pipeline

### 1. Trajectory preprocessing

`01_preprocess.sh` applies:

1. periodic-boundary no-jump correction;
2. molecular centering; and
3. rotational/translational fitting.

The resulting processed trajectory is used by downstream analyses.

### 2. Basic molecular-dynamics descriptors

`02_basic_analysis.sh` calculates:

- **RMSD** — structural deviation relative to the reference structure;
- **RMSF** — residue-level positional fluctuation;
- **Radius of gyration** — global compactness;
- **SASA** — solvent exposure; and
- **intra-protein hydrogen bonds** — persistent/non-persistent internal interactions.

### 3. Principal Component Analysis

PCA is performed using GROMACS covariance/eigenvector analysis to characterize dominant collective motions and reduced-dimensional conformational space.

### 4. Free Energy Landscape

The pipeline derives a two-dimensional free-energy landscape from PC1/PC2 sampling using Boltzmann inversion:

$$
G(x,y) = -k_B T \ln P(x,y)
$$

where `P(x,y)` represents the estimated joint probability density and `T` is the configured simulation temperature.

Both 2D and 3D FEL visualizations are generated.

### 5. DSSP secondary structure

GROMACS `gmx dssp` is used to assign secondary-structure states over the trajectory. The resulting residue × frame information is visualized as a temporal heatmap.

### 6. Dynamic Cross-Correlation Matrix

DCCM analysis is performed using MDAnalysis on C-alpha displacement trajectories.

$$
C_{ij} = \frac{\langle \Delta \mathbf r_i \cdot \Delta \mathbf r_j \rangle}
{\sqrt{\langle |\Delta \mathbf r_i|^2 \rangle\langle |\Delta \mathbf r_j|^2 \rangle}}
$$

Values approach `+1` for strongly correlated motion and `-1` for strongly anti-correlated motion.

### 7. Statistical comparison

`04_statistics.R` applies the **Kruskal–Wallis H-test** to compare the distributions of RMSD, RMSF, SASA, hydrogen bonds and radius of gyration across systems.

Results are saved as:

```text
outputs/statistics/kruskal_results.csv
```

The default significance threshold is `p < 0.05`.

> **Important statistical note:** the Kruskal–Wallis test evaluates distributional differences between groups. It does not by itself establish biological significance, causal mechanisms, or independence of individual trajectory frames. Researchers should account for trajectory autocorrelation and study design when performing publication-grade statistical inference.

---

## Generated figures

`05_plots.py` produces high-resolution PNG figures at 300 DPI, including:

### Per-system figures

- RMSD
- RMSF
- SASA
- radius of gyration
- PCA conformational-space plots
- 2D FEL
- 3D FEL
- DSSP heatmap
- DCCM heatmap

### Comparative figures

For multi-system runs, the pipeline additionally produces overlays such as:

- RMSD comparison
- RMSF comparison
- SASA comparison
- radius-of-gyration comparison
- hydrogen-bond comparison

Exact figure count depends on the number of detected systems and which analysis outputs are available.

---

## Numerical reporting

`report_generator.py` consolidates calculated descriptors into structured text reports containing numerical summaries for the analyzed systems, including available:

- RMSD statistics
- RMSF statistics
- Rg statistics
- SASA statistics
- hydrogen-bond statistics
- PCA variance information
- DSSP secondary-structure fractions
- DCCM summary statistics
- Kruskal–Wallis results

This report is also used as structured input for the interpretation stage.

---

## Local LLM interpretation

The optional `06_llm_interpretation.py` module uses the local Ollama API to transform calculated numerical summaries into a structured scientific interpretation.

The model is prompted to discuss topics including:

- structural stability from RMSD;
- flexible regions from RMSF;
- compactness from Rg;
- solvent exposure from SASA;
- hydrogen-bond changes;
- dominant motions from PCA;
- conformational basins from FEL;
- secondary-structure behavior from DSSP; and
- correlated/anti-correlated motions from DCCM.

Output:

```text
outputs/llm/interpretation.txt
```

### Why local LLM inference?

The pipeline is designed to keep analysis data local when Ollama is used locally. No external hosted LLM API is required by the interpretation module.

However, **LLM output should be treated as an assisted interpretation layer, not as experimental evidence or an independent validation method.** Numerical results should always be inspected by the researcher before being used in a manuscript.

---

## Manuscript generation

`07_paper_builder.py` uses the numerical report and LLM interpretation to generate a draft scientific document containing:

- Methods-style descriptions of the implemented analyses;
- Results & Discussion-style interpretation;
- discussion of RMSD, RMSF, Rg, SASA and hydrogen bonds;
- PCA/FEL interpretation;
- DSSP and DCCM interpretation; and
- statistical results.

The generated document is a **drafting aid**. It should be scientifically reviewed, corrected, referenced and edited by the authors before submission.

---

## Reproducibility considerations

For reproducible research, record at minimum:

- GROMACS version;
- MD-POST commit/tag;
- Conda environment specification;
- simulation temperature;
- force field and simulation protocol;
- trajectory length and sampling interval;
- system-specific index groups;
- preprocessing choices; and
- Ollama model/version when LLM-assisted text is used.

The pipeline automates analysis execution, but reproducibility ultimately depends on the quality and documentation of the upstream molecular-dynamics simulations.

---

## Limitations

MD-POST intentionally automates a broad analysis workflow, but it does not remove the need for scientific judgment.

Key limitations include:

1. **Trajectory quality matters.** Poor equilibration, insufficient sampling, inappropriate force fields or problematic structures can produce misleading downstream results.
2. **Default GROMACS groups may not fit every system.** Custom index groups should be reviewed for complexes, membrane proteins, multi-chain systems and unusual topologies.
3. **Trajectory frames are not necessarily independent observations.** Time-series autocorrelation should be considered when interpreting statistical tests.
4. **Kruskal–Wallis is not a complete post-hoc analysis.** Significant results may require appropriate pairwise/post-hoc testing and effect-size reporting.
5. **FEL interpretation depends on sampling.** Sparse or poorly converged conformational sampling can distort estimated probability landscapes.
6. **DCCM is descriptive.** Correlation does not establish causality or an allosteric mechanism by itself.
7. **LLM interpretation can be wrong.** Generated prose must be checked against the numerical data and relevant literature.
8. **Mock data are for software testing only.** They must never be presented as simulation-derived evidence.

---

## Intended use

MD-POST is intended for:

- academic molecular-dynamics studies;
- comparative apo/ligand-bound analyses;
- mutant vs wild-type comparisons;
- multi-condition trajectory analysis;
- computational drug-discovery workflows;
- reproducible research-software development; and
- rapid preparation of analysis summaries and manuscript drafts.

It is **not** intended to replace expert trajectory inspection, statistical consultation, experimental validation, or peer review.

---

## Software stack

| Component | Role |
|---|---|
| **GROMACS** | Trajectory preprocessing and core MD analyses |
| **Python** | Data processing, advanced analyses, plotting and reporting |
| **MDAnalysis** | Trajectory handling and DCCM calculation |
| **MDTraj** | Additional trajectory-analysis support |
| **R / tidyverse** | Statistical analysis |
| **Matplotlib / Seaborn** | Visualization |
| **PyMOL** | Molecular visualization/manual inspection |
| **Ollama** | Optional local LLM inference |
| **Conda** | Environment management |

---

## Citation

If you use MD-POST in academic work, please cite the software repository and the underlying scientific tools used in your analysis.

### MD-POST

```bibtex
@software{nalgirkar_md_post_2026,
  author  = {Nalgirkar, Harsh},
  title   = {MD-POST: Automated Multi-System GROMACS Molecular Dynamics Post-Processing and AI-Assisted Interpretation Pipeline},
  version = {2.0.0},
  year    = {2026},
  url     = {https://github.com/nalgirkarh-prog/MD-POST_PROCESSING_UNIT-MPU-}
}
```

### GROMACS

```bibtex
@article{abraham2015gromacs,
  title   = {GROMACS: High performance molecular simulations through multi-level parallelism from laptops to supercomputers},
  author  = {Abraham, Mark James and Murtola, Teemu and Schulz, Roland and P{\'a}ll, Szil{\'a}rd and Smith, Jeremy C and Hess, Berk and Lindahl, Erik},
  journal = {SoftwareX},
  volume  = {1},
  pages   = {19--25},
  year    = {2015}
}
```

### MDAnalysis

```bibtex
@article{michaud2011mdanalysis,
  title   = {MDAnalysis: A toolkit for the analysis of molecular dynamics simulations},
  author  = {Michaud-Agrawal, Naveen and Denning, Elizabeth J. and Woolf, Thomas B. and Beckstein, Oliver},
  journal = {Journal of Computational Chemistry},
  volume  = {32},
  number  = {10},
  pages   = {2319--2327},
  year    = {2011}
}
```

### Ollama

Ollama is used as the local inference layer for optional AI-assisted interpretation. Cite the specific model and version used in your work where appropriate.

---

## Versioning

Current development version:

**MD-POST v2.0.0**

The v2 workflow focuses on a more integrated multi-system analysis architecture, expanded advanced analysis, automated numerical reporting, local LLM interpretation and manuscript-draft generation.

Future development may include:

- trajectory convergence diagnostics;
- improved replicate-aware statistics;
- automated pairwise post-hoc testing;
- confidence intervals and effect sizes;
- additional collective-variable analyses;
- richer report schemas;
- containerized execution; and
- automated validation/test suites.

---

## License

This project is distributed under the license included in [`LICENSE`](LICENSE).

---

## Author

**Harsh Nalgirkar**
B.Pharm Student · Computational Drug Discovery Researcher · Research Software Developer

GitHub: `https://github.com/nalgirkarh-prog`
