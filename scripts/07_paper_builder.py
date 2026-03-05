import os
import ollama

BASE_DIR = "outputs"
PAPER_DIR = os.path.join(BASE_DIR, "paper")
LLM_DIR = os.path.join(BASE_DIR, "llm")

os.makedirs(PAPER_DIR, exist_ok=True)

interpretation_file = os.path.join(LLM_DIR, "interpretation.txt")

if not os.path.exists(interpretation_file):
    raise FileNotFoundError("interpretation.txt not found. Run 06_llm_interpretation.py first.")

with open(interpretation_file) as f:
    interpretation = f.read()


###############################################
# EXPAND INTERPRETATION INTO JOURNAL TEXT
###############################################

paper_prompt = f"""
You are an expert scientific writer specializing in molecular dynamics
and structural biology.

Expand the following MD interpretation into a **detailed journal-style
Results and Discussion section**.

Requirements:

• Write in clear scientific narrative form
• Avoid bullet points
• Explain each concept clearly so that even a non-science reader
  can understand the meaning
• Interpret the results biologically
• Compare the different systems where possible
• Discuss implications of RMSD, RMSF, Rg, SASA, PCA, FEL and DSSP
• Explain what the results suggest about structural stability
• Explain conformational dynamics
• Explain possible biological implications of the observed dynamics

Target length: **1500–2500 words**

Interpretation to expand:

{interpretation}
"""

print("Generating expanded Results and Discussion using LLM...")

response = ollama.chat(
    model="llama3",
    options={
        "temperature":0.3,
        "num_predict":3000
    },
    messages=[
        {
            "role":"system",
            "content":"You are an expert structural biologist and scientific writer."
        },
        {
            "role":"user",
            "content":paper_prompt
        }
    ]
)

results_section = response["message"]["content"]


###############################################
# METHODS SECTION
###############################################

methods = """
Molecular Dynamics Simulation Analysis

All molecular dynamics trajectory analyses were performed using the
MD-POST automated analysis pipeline developed for systematic analysis
of protein–ligand simulation trajectories.

Structural stability of each system was evaluated using the root mean
square deviation (RMSD) of backbone atoms relative to the starting
structure. RMSD provides a quantitative measure of how much the protein
structure deviates over the course of the simulation and is widely used
to assess the overall stability of molecular systems.

Local residue-level flexibility was quantified using root mean square
fluctuation (RMSF) calculations. RMSF measures the extent of positional
variation of each residue throughout the simulation trajectory and
allows identification of flexible loops or rigid structural regions.

Global structural compactness of the protein was assessed using the
radius of gyration (Rg). This metric describes the distribution of
atoms around the center of mass of the protein and provides insight
into folding stability and structural compactness during the simulation.

Solvent accessibility changes were evaluated using solvent accessible
surface area (SASA) calculations. SASA reflects the extent to which
protein surfaces remain exposed to the solvent environment and can
indicate conformational changes that alter solvent exposure.

Hydrogen bonding patterns were analyzed using the GROMACS hydrogen
bond analysis module to evaluate intermolecular interactions that
contribute to structural stabilization of the system.

Principal Component Analysis (PCA) was performed on the covariance
matrix of atomic fluctuations to identify dominant collective motions
within the protein structure. PCA reduces complex molecular motions
into a smaller number of principal components that describe the
largest amplitude conformational changes observed during the
simulation.

Free Energy Landscapes (FEL) were constructed using projections
along the first two principal components. The FEL provides a
thermodynamic representation of conformational states sampled
during the simulation and enables identification of energetically
favorable structural basins.

Secondary structure evolution throughout the simulation was analyzed
using the DSSP algorithm, which assigns secondary structure elements
such as alpha helices, beta sheets, and turns based on hydrogen
bonding patterns and backbone geometry.

All plots and structural analyses were generated automatically
through the MD-POST pipeline to ensure reproducibility and
consistent analysis across all simulated systems.
"""


###############################################
# TITLE
###############################################

title = "Comparative Molecular Dynamics Analysis of Protein Systems Using an Automated MD-POST Pipeline"


###############################################
# TEXT PAPER VERSION
###############################################

txt_paper = f"""
{title}

RESULTS AND DISCUSSION

{results_section}

METHODS

{methods}
"""


###############################################
# MARKDOWN PAPER VERSION
###############################################

md_paper = f"""
# {title}

## Results and Discussion

{results_section}

## Methods

{methods}
"""


###############################################
# LATEX PAPER VERSION
###############################################

tex_paper = f"""
\\section{{Results and Discussion}}

{results_section}

\\section{{Methods}}

{methods}
"""


###############################################
# WRITE FILES
###############################################

with open(os.path.join(PAPER_DIR, "paper_draft.txt"), "w") as f:
    f.write(txt_paper)

with open(os.path.join(PAPER_DIR, "paper_draft.md"), "w") as f:
    f.write(md_paper)

with open(os.path.join(PAPER_DIR, "paper_draft.tex"), "w") as f:
    f.write(tex_paper)


print("Paper drafts generated:")
print(" - outputs/paper/paper_draft.txt")
print(" - outputs/paper/paper_draft.md")
print(" - outputs/paper/paper_draft.tex")
