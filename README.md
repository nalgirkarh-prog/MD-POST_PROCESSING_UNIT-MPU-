MD-Post: Automated MD Analysis & LLM-Assisted Interpretation 🧬🤖
MD-Post is an end-to-end, multi-system post-processing pipeline for GROMACS molecular dynamics simulations. It streamlines the workflow from raw trajectories to statistical validation and generates a draft manuscript ("pseudo-paper") using a local LLM.

🚀 Key Features
Agnostic File Handling: Automatically detects .gro, .tpr, .xtc, and .top files based on extensions—no strict naming conventions required.

Multi-System Comparison: Processes multiple folders simultaneously (e.g., APO, COMPLEX, MUTANT), producing individual and overlay plots.

Advanced Analysis:

Basic: RMSD, RMSF, Radius of Gyration (Rg), SASA, H-Bonds.

Advanced: Principal Component Analysis (PCA), Free Energy Landscapes (FEL), DSSP (Secondary Structure), and DCCM (Cross-Correlation).

Statistical Rigor: Performs Kruskal-Wallis non-parametric testing to determine significance between different systems.

AI Interpretation: Integrates with Ollama (Llama 3) to interpret .xvg data and draft a discussion section.

📁 Repository Structure
Plaintext
.
├── config/                 # Pipeline parameters (time ranges, etc.)
├── input/                  # DROP FOLDERS HERE (e.g., ./input/APO/, ./input/Complex/)
├── scripts/                # 01-07 processing logic
├── environment.yml         # Conda environment definition
├── run_pipeline.sh         # Main entry point
└── clean_workspace.sh      # Utility to reset the workspace
⚙️ Installation & Setup
1. Prerequisites
Install Ollama and pull the Llama 3 model:

Bash
ollama pull llama3
2. Environment Setup
Clone the repository and build the md_pipeline environment:

Bash
git clone https://github.com/YOUR_USERNAME/md_post.git
cd md_post
conda env create -f environment.yml
conda activate md_pipeline
🏃 Usage
Place your system folders inside the input/ directory. Each folder should contain one of each: .gro, .tpr, .xtc, and .top.

Execute the pipeline:

Bash
bash run_pipeline.sh
Check the outputs/ folder for .xvg data and the figures/ folder for system-labeled graphs (e.g., APO_RMSD.png).

To clean the pipeline after one run to make it as before, execute
bash clean_workspace.sh 

Review the generated pseudo_paper.md for AI-assisted insights.

📊 Statistical Methodology
For inter-system comparisons, this pipeline employs the Kruskal-Wallis H-test. This non-parametric approach is used to assess if the distribution of properties (like SASA or RMSD) differs significantly across the simulated ensembles without assuming a normal distribution.


✍️ Credits & Citations
If you use this pipeline in your research, please cite the original author and the underlying tools:

Tooling Citations
GROMACS: Abraham, M. J., et al. (2015). GROMACS: High performance molecular simulations through multi-level parallelism from laptops to supercomputers. SoftwareX.

Ollama: Ollama Team. (2024). Local Large Language Model Runner.

MD-Post Pipeline: [Your Name/Handle], (2026). MD-Post: Automated MD Analysis & Interpretation. GitHub Repository.

BibTeX
Code snippet
@software{harsh_md_post_2026,
  author = {Harsh [Your Last Name]},
  title = {MD-Post: Automated MD Analysis and LLM-Assisted Interpretation Pipeline},
  url = {https://github.com/YOUR_USERNAME/md_post},
  version = {1.0.0},
  year = {2026}
}

@article{gromacs2015,
  title={GROMACS: High performance molecular simulations through multi-level parallelism from laptops to supercomputers},
  author={Abraham, Mark James and Murtola, Teemu and Schulz, Roland and Páll, Szilárd and Smith, Jeremy C and Hess, Berk and Lindahl, Erik},
  journal={SoftwareX},
  volume={1},
  pages={19--25},
  year={2015},
  publisher={Elsevier}
}
