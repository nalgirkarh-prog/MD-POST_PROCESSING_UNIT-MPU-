import os
import pandas as pd
import numpy as np

OUTPUT_ROOT = "outputs"
REPORT_DIR = os.path.join(OUTPUT_ROOT, "final_report")
os.makedirs(REPORT_DIR, exist_ok=True)

report_path = os.path.join(REPORT_DIR, "analysis_report.txt")

def load_xvg(path):
    data = []
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                if not line.startswith(("#", "@")):
                    parts = line.split()
                    if len(parts) >= 2:
                        data.append(float(parts[1]))
    return np.array(data)

def load_dssp_stats(path):
    if not os.path.exists(path):
        return None
    frames = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(("#", "@")):
                continue
            frames.append(line)
    if not frames:
        return None

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

    counts = {}
    total_chars = 0
    for frame in frames:
        for char in frame:
            full_name = ss_names.get(char, 'Coil/Loop')
            counts[full_name] = counts.get(full_name, 0) + 1
            total_chars += 1

    percentages = {name: (count / total_chars) * 100 for name, count in counts.items()}
    return percentages

def load_dccm_stats(path):
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
        "high_pos_fraction": high_pos_fraction,
        "high_neg_fraction": high_neg_fraction
    }

systems = [
    d for d in os.listdir(OUTPUT_ROOT)
    if os.path.isdir(os.path.join(OUTPUT_ROOT, d))
    and d not in ["combined", "statistics", "final_report", "llm", "paper"]
]

metrics = ["rmsd", "rmsf", "sasa", "hbond", "rg"]

with open(report_path, "w") as f:
    f.write("MD-POST Multi-System Analysis Report\n")
    f.write("="*60 + "\n\n")

    # -------------------------------
    # Per-system Analysis
    # -------------------------------
    f.write("PER-SYSTEM SUMMARY STATISTICS\n")
    f.write("-"*60 + "\n\n")

    for system in systems:
        f.write(f"SYSTEM: {system}\n")
        f.write("-"*40 + "\n")

        for metric in metrics:
            xvg_path = os.path.join(
                OUTPUT_ROOT, system, metric, f"{metric}.xvg"
            )

            if os.path.exists(xvg_path):
                values = load_xvg(xvg_path)
                if len(values) > 0:
                    mean = np.mean(values)
                    median = np.median(values)
                    std = np.std(values)
                    vmin = np.min(values)
                    vmax = np.max(values)

                    f.write(f"{metric.upper()}:\n")
                    f.write(f"  Mean   : {mean:.4f}\n")
                    f.write(f"  Median : {median:.4f}\n")
                    f.write(f"  Std Dev: {std:.4f}\n")
                    f.write(f"  Min    : {vmin:.4f}\n")
                    f.write(f"  Max    : {vmax:.4f}\n\n")

        # Secondary Structure (DSSP)
        dssp_path = os.path.join(OUTPUT_ROOT, system, "dssa", "dssp.dat")
        dssp_res = load_dssp_stats(dssp_path)
        if dssp_res:
            f.write("SECONDARY STRUCTURE (DSSP) FRACTION:\n")
            for ss_name, pct in sorted(dssp_res.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {ss_name:18}: {pct:.2f}%\n")
            f.write("\n")

        # Dynamic Cross-Correlation (DCCM)
        dccm_path = os.path.join(OUTPUT_ROOT, system, "dccm", "dccm.csv")
        dccm_res = load_dccm_stats(dccm_path)
        if dccm_res:
            f.write("DYNAMIC CROSS-CORRELATION (DCCM) ANALYSIS:\n")
            f.write(f"  Mean Off-Diagonal Correlation : {dccm_res['mean_off_diag']:.4f}\n")
            f.write(f"  Mean Positive Correlation     : {dccm_res['mean_pos']:.4f}\n")
            f.write(f"  Mean Negative Correlation     : {dccm_res['mean_neg']:.4f}\n")
            f.write(f"  Strong Positive Corr. (>0.7)  : {dccm_res['high_pos_fraction']*100:.2f}%\n")
            f.write(f"  Strong Negative Corr. (<-0.4) : {dccm_res['high_neg_fraction']*100:.2f}%\n")
            f.write("\n")

        f.write("\n")

    # -------------------------------
    # Comparative Statistics
    # -------------------------------
    f.write("\nCOMPARATIVE STATISTICS\n")
    f.write("-"*60 + "\n\n")

    stats_path = os.path.join(OUTPUT_ROOT, "statistics", "kruskal_results.csv")

    if os.path.exists(stats_path):
        stats = pd.read_csv(stats_path)
        for _, row in stats.iterrows():
            p = row["p_value"]
            significance = "Significant" if p < 0.05 else "Not Significant"
            f.write(f"{row['Metric'].upper()}:\n")
            f.write(f"  Kruskal-Wallis p-value: {p:.6f}\n")
            f.write(f"  Interpretation: {significance}\n\n")
    else:
        f.write("No statistical results found.\n")

print("Report generated successfully.")
