import os
import ollama
import numpy as np

BASE_DIR = "outputs"
IGNORE = {"statistics", "llm", "paper", "final_report", "combined"}

# Configure the LLM model to use (default to lightweight llama3.2 for CPU-friendly runs)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

def read_xvg(path):
    data = []
    if not os.path.exists(path):
        return np.array([])
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(("@", "#")) or not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                try:
                    data.append(float(parts[1]))
                except ValueError:
                    continue
    return np.array(data)


def summarize_pca(path):
    x = []
    y = []
    if not os.path.exists(path):
        return None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(("@", "#")) or not line:
                continue
            p = line.split()
            if len(p) >= 3:
                try:
                    x.append(float(p[1]))
                    y.append(float(p[2]))
                except ValueError:
                    continue
            elif len(p) == 2:
                try:
                    x.append(float(p[0]))
                    y.append(float(p[1]))
                except ValueError:
                    continue
    if len(x) == 0:
        return None
    return {
        "pc1_var": np.var(x),
        "pc2_var": np.var(y)
    }


def summarize_dssp(path):
    if not os.path.exists(path):
        return {}
    counts = {}
    total = 0
    ss_names = {
        'H': 'Alpha Helix',
        'E': 'Beta Sheet',
        'T': 'Turn',
        'S': 'Bend',
        'G': '3-10 Helix',
        'B': 'Beta Bridge',
        'I': 'Pi Helix',
        'P': 'Polyproline II',
        '~': 'Coil/Loop',
        ' ': 'Coil/Loop'
    }
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(("#", "@")) or not line:
                continue
            for c in line:
                name = ss_names.get(c, 'Coil/Loop')
                counts[name] = counts.get(name, 0) + 1
                total += 1
    if total == 0:
        return {}
    return {k: f"{(v/total)*100:.2f}%" for k, v in counts.items()}


def summarize_dccm(path):
    if not os.path.exists(path):
        return None
    try:
        matrix = np.loadtxt(path, delimiter=",")
    except Exception:
        return None
    n = matrix.shape[0]
    if n <= 1:
        return None
    mask = ~np.eye(n, dtype=bool)
    off_diag = matrix[mask]

    mean_corr = np.mean(off_diag)
    mean_pos = np.mean(off_diag[off_diag > 0]) if np.any(off_diag > 0) else 0.0
    mean_neg = np.mean(off_diag[off_diag < 0]) if np.any(off_diag < 0) else 0.0
    high_pos_fraction = np.sum(off_diag > 0.7) / len(off_diag)
    high_neg_fraction = np.sum(off_diag < -0.4) / len(off_diag)

    return {
        "mean_off_diag": mean_corr,
        "mean_pos": mean_pos,
        "mean_neg": mean_neg,
        "high_pos_percent": f"{high_pos_fraction*100:.2f}%",
        "high_neg_percent": f"{high_neg_fraction*100:.2f}%"
    }


systems = [s for s in os.listdir(BASE_DIR)
           if os.path.isdir(os.path.join(BASE_DIR, s))
           and s not in IGNORE]

analysis_summary = ""
print("Detected systems for LLM interpretation:", systems)

for system in systems:
    sys_dir = os.path.join(BASE_DIR, system)

    rmsd_file = os.path.join(sys_dir, "rmsd", "rmsd.xvg")
    rmsf_file = os.path.join(sys_dir, "rmsf", "rmsf.xvg")
    rg_file = os.path.join(sys_dir, "rg", "rg.xvg")
    sasa_file = os.path.join(sys_dir, "sasa", "sasa.xvg")
    hbond_file = os.path.join(sys_dir, "hbond", "hbond.xvg")

    pca_file = os.path.join(sys_dir, "pca", "projection.xvg")
    dssp_file = os.path.join(sys_dir, "dssa", "dssp.dat")
    dccm_file = os.path.join(sys_dir, "dccm", "dccm.csv")

    summary = f"\nSystem: {system}\n"

    rmsd = read_xvg(rmsd_file)
    if len(rmsd) > 0:
        summary += f"RMSD mean: {np.mean(rmsd):.3f} nm, SD: {np.std(rmsd):.3f} nm\n"

    rmsf = read_xvg(rmsf_file)
    if len(rmsf) > 0:
        summary += f"RMSF mean: {np.mean(rmsf):.3f} nm, Max: {np.max(rmsf):.3f} nm\n"

    rg = read_xvg(rg_file)
    if len(rg) > 0:
        summary += f"Radius of gyration mean: {np.mean(rg):.3f} nm\n"

    sasa = read_xvg(sasa_file)
    if len(sasa) > 0:
        summary += f"SASA mean: {np.mean(sasa):.3f} nm²\n"

    hbond = read_xvg(hbond_file)
    if len(hbond) > 0:
        summary += f"Intra-protein H-bonds mean: {np.mean(hbond):.1f}\n"

    pca = summarize_pca(pca_file)
    if pca:
        summary += f"PCA variance PC1: {pca['pc1_var']:.3f}, PC2: {pca['pc2_var']:.3f}\n"

    dssp = summarize_dssp(dssp_file)
    if dssp:
        summary += f"Secondary structure fraction: {dssp}\n"

    dccm = summarize_dccm(dccm_file)
    if dccm:
        summary += (f"DCCM correlation: Mean={dccm['mean_off_diag']:.3f}, "
                    f"Pos={dccm['mean_pos']:.3f}, Neg={dccm['mean_neg']:.3f}, "
                    f"StrongPos={dccm['high_pos_percent']}, StrongNeg={dccm['high_neg_percent']}\n")

    analysis_summary += summary

prompt = f"""
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
9. What DCCM reveals about correlated and anti-correlated residue motions.

Explain the **biological meaning** of each observation.
Avoid generic statements.

When comparing systems, clearly state:
• which system is most stable
• which is most flexible
• which shows the most stable energy basin
• which has the most highly correlated/synchronized internal motions

Write 6–8 paragraphs per system.

Simulation data:

{analysis_summary}
"""

print(f"Connecting to local Ollama API (using model: {OLLAMA_MODEL})...")
try:
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system",
             "content": "You are a molecular dynamics expert. Provide cautious scientific interpretation."},
            {"role": "user", "content": prompt}
        ]
    )

    os.makedirs("outputs/llm", exist_ok=True)
    with open("outputs/llm/interpretation.txt", "w") as f:
        f.write(response["message"]["content"])

    print("LLM interpretation saved to outputs/llm/interpretation.txt")
except Exception as e:
    print(f"❌ Ollama interaction failed: {e}")
    print("Please make sure the Ollama server is running (e.g. run 'ollama serve' in background) and the model is pulled.")
