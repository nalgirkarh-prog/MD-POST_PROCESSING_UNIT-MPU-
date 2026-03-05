import os
import ollama
import numpy as np

BASE_DIR = "outputs"
IGNORE = {"statistics","llm","paper","final_report"}

def read_xvg(path):
    data = []
    with open(path) as f:
        for line in f:
            if line.startswith(("@","#")):
                continue
            data.append(float(line.split()[1]))
    return np.array(data)


def summarize_pca(path):

    x=[]
    y=[]

    with open(path) as f:
        for line in f:
            if line.startswith(("@","#")):
                continue

            p=line.split()

            if len(p)<3:
                continue

            x.append(float(p[1]))
            y.append(float(p[2]))

    if len(x)==0:
        return None

    return {
        "pc1_var":np.var(x),
        "pc2_var":np.var(y)
    }


def summarize_dssp(path):

    counts={}

    with open(path) as f:
        for line in f:

            if line.startswith("#"):
                continue

            ss=line.strip()

            for c in ss:

                counts[c]=counts.get(c,0)+1

    return counts


systems=[s for s in os.listdir(BASE_DIR)
         if os.path.isdir(os.path.join(BASE_DIR,s))
         and s not in IGNORE]


analysis_summary=""

print("Detected systems:",systems)

for system in systems:

    sys_dir=os.path.join(BASE_DIR,system)

    rmsd_file=os.path.join(sys_dir,"rmsd","rmsd.xvg")
    rmsf_file=os.path.join(sys_dir,"rmsf","rmsf.xvg")
    rg_file=os.path.join(sys_dir,"rg","rg.xvg")
    sasa_file=os.path.join(sys_dir,"sasa","sasa.xvg")

    pca_file=os.path.join(sys_dir,"pca","projection.xvg")
    dssp_file=os.path.join(sys_dir,"dssa","dssp.dat")
    fel_file=os.path.join(sys_dir,"fel","fel.xpm")

    summary=f"\nSystem: {system}\n"

    if os.path.exists(rmsd_file):

        rmsd=read_xvg(rmsd_file)

        summary+=f"""
RMSD mean: {np.mean(rmsd):.3f} nm
RMSD SD: {np.std(rmsd):.3f} nm
"""

    if os.path.exists(rmsf_file):

        rmsf=read_xvg(rmsf_file)

        summary+=f"""
RMSF mean: {np.mean(rmsf):.3f} nm
RMSF max: {np.max(rmsf):.3f} nm
"""

    if os.path.exists(rg_file):

        rg=read_xvg(rg_file)

        summary+=f"""
Radius of gyration mean: {np.mean(rg):.3f} nm
"""

    if os.path.exists(sasa_file):

        sasa=read_xvg(sasa_file)

        summary+=f"""
SASA mean: {np.mean(sasa):.3f} nm²
"""

    if os.path.exists(pca_file):

        pca=summarize_pca(pca_file)

        if pca:

            summary+=f"""
PCA variance PC1: {pca['pc1_var']:.3f}
PCA variance PC2: {pca['pc2_var']:.3f}
"""

    if os.path.exists(dssp_file):

        dssp=summarize_dssp(dssp_file)

        summary+=f"""
Secondary structure counts: {dssp}
"""

    if os.path.exists(fel_file):

        summary+=f"""
Free energy landscape generated from PCA projection.
"""

    analysis_summary+=summary


prompt=f"""
You are a senior structural biologist writing a detailed explanation of
molecular dynamics simulation results.

Your goal is to explain the findings in a way that is BOTH:

• scientifically rigorous
• understandable even to a non-science reader

Write in a narrative style, not bullet points.

For EACH system explain:

1. What RMSD means in simple language.
2. What the RMSD value suggests about structural stability.
3. What RMSF reveals about flexible regions.
4. What the radius of gyration tells us about protein compactness.
5. What SASA changes imply about solvent exposure.
6. What PCA indicates about dominant motions.
7. What the free energy landscape reveals about conformational states.
8. What DSSP results say about secondary structure stability.

Explain the **biological meaning** of each observation.

Avoid generic statements.

When comparing systems, clearly state:

• which system is most stable
• which is most flexible
• which shows the most stable energy basin

Write 6–8 paragraphs per system.

Simulation data:

{analysis_summary}
"""


response=ollama.chat(
    model="llama3",
    messages=[
        {"role":"system",
         "content":"You are a molecular dynamics expert. Provide cautious scientific interpretation."},
        {"role":"user","content":prompt}
    ]
)

os.makedirs("outputs/llm",exist_ok=True)

with open("outputs/llm/interpretation.txt","w") as f:
    f.write(response["message"]["content"])

print("LLM interpretation saved to outputs/llm/interpretation.txt")
