import os
import pandas as pd
import numpy as np

OUTPUT_ROOT = "outputs"
REPORT_DIR = os.path.join(OUTPUT_ROOT, "final_report")
os.makedirs(REPORT_DIR, exist_ok=True)

report_path = os.path.join(REPORT_DIR, "analysis_report.txt")

def load_xvg(path):
    data = []
    with open(path) as f:
        for line in f:
            if not line.startswith(("#", "@")):
                parts = line.split()
                if len(parts) >= 2:
                    data.append(float(parts[1]))
    return np.array(data)

systems = [
    d for d in os.listdir(OUTPUT_ROOT)
    if os.path.isdir(os.path.join(OUTPUT_ROOT, d))
    and d not in ["combined", "statistics", "final_report"]
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
