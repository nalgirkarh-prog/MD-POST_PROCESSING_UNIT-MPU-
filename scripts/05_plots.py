import os
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend — required for headless/server runs
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import matplotlib.colors as mcolors

OUTPUT_DIR = "outputs"
FIG_DIR = "figures"

os.makedirs(FIG_DIR, exist_ok=True)

# Detect systems
systems = [
    d for d in os.listdir(OUTPUT_DIR)
    if os.path.isdir(os.path.join(OUTPUT_DIR, d))
    and d not in ["statistics", "llm", "final_report", "paper", "combined"]
]

print("Detected systems for plotting:", systems)

# XVG Reader (robust to comments, empty lines)
def read_xvg(file):
    data = []
    with open(file) as f:
        for line in f:
            line = line.strip()
            if line.startswith(("#", "@")) or not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                try:
                    data.append([float(parts[0]), float(parts[1])])
                except ValueError:
                    continue
    return np.array(data)

# PCA Reader (robust column reading)
def read_pca_projection(file):
    pc1 = []
    pc2 = []
    with open(file) as f:
        for line in f:
            line = line.strip()
            if line.startswith(("#", "@")) or not line:
                continue
            parts = line.split()
            if len(parts) >= 3:
                try:
                    pc1.append(float(parts[1]))
                    pc2.append(float(parts[2]))
                except ValueError:
                    continue
            elif len(parts) == 2:
                try:
                    pc1.append(float(parts[0]))
                    pc2.append(float(parts[1]))
                except ValueError:
                    continue
    return np.array(pc1), np.array(pc2)

# Compute FEL from PCA projection
def compute_fel(pc1, pc2, temp=300):
    hist, xedges, yedges = np.histogram2d(pc1, pc2, bins=50)
    prob = hist / np.sum(hist)
    prob = np.where(prob > 0, prob, np.nan)
    kB = 0.008314462 # kJ/(mol*K)
    G = -kB * temp * np.log(prob)
    G -= np.nanmin(G)
    x_centers = (xedges[:-1] + xedges[1:]) / 2
    y_centers = (yedges[:-1] + yedges[1:]) / 2
    max_energy = np.nanmax(G)
    G_filled = np.nan_to_num(G, nan=max_energy + 2.0)
    return x_centers, y_centers, G_filled

# Plot FEL
def plot_fel(projection_file, system, fig_dir):
    if not os.path.exists(projection_file):
        return
    pc1, pc2 = read_pca_projection(projection_file)
    if len(pc1) < 10:
        return
    x_centers, y_centers, G = compute_fel(pc1, pc2)
    X, Y = np.meshgrid(x_centers, y_centers)

    # 2D Contour
    plt.figure(figsize=(7, 6))
    contour = plt.contourf(X, Y, G.T, levels=30, cmap="jet")
    plt.title(f"{system} Free Energy Landscape")
    plt.xlabel("PC1 (nm)")
    plt.ylabel("PC2 (nm)")
    cbar = plt.colorbar(contour)
    cbar.set_label("Free Energy (kJ/mol)")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{fig_dir}/{system}_FEL_2D.png", dpi=300)
    plt.close()

    # 3D Surface
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(X, Y, G.T, cmap="jet", linewidth=0, antialiased=True, rcount=50, ccount=50)
    offset = np.nanmin(G)
    ax.contourf(X, Y, G.T, zdir='z', offset=offset, cmap="jet", levels=20, alpha=0.5)
    ax.set_title(f"{system} Free Energy Landscape (3D)")
    ax.set_xlabel("PC1 (nm)")
    ax.set_ylabel("PC2 (nm)")
    ax.set_zlabel("Free Energy (kJ/mol)")
    ax.set_zlim(offset, np.nanmax(G) + 1.0)
    fig.colorbar(surf, ax=ax, label="Free Energy (kJ/mol)", shrink=0.6)
    plt.tight_layout()
    plt.savefig(f"{fig_dir}/{system}_FEL.png", dpi=300)
    plt.close()

# Plot DSSP heatmap
def plot_dssp_heatmap(dssp_file, system, fig_dir):
    if not os.path.exists(dssp_file):
        return
    frames = []
    with open(dssp_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith(("#", "@")) or not line:
                continue
            frames.append(line)
    if not frames:
        return
    n_frames = len(frames)
    n_residues = len(frames[0])

    ss_map = {
        '~': 0, ' ': 0, 'C': 0,
        'H': 1, 'E': 2, 'T': 3, 'S': 4,
        'G': 5, 'B': 6, 'I': 7, 'P': 8
    }

    data = np.zeros((n_residues, n_frames))
    for f_idx, frame in enumerate(frames):
        for r_idx, char in enumerate(frame):
            if r_idx < n_residues:
                data[r_idx, f_idx] = ss_map.get(char, 0)

    plt.figure(figsize=(10, 6))
    colors_list = [
        '#d3d3d3', '#e0115f', '#0000ff', '#008000',
        '#ffa500', '#800080', '#00ffff', '#ff00ff', '#ffc0cb'
    ]
    unique_vals = np.unique(data).astype(int)
    cmap = mcolors.ListedColormap([colors_list[v] for v in unique_vals])

    im = plt.imshow(data, aspect='auto', interpolation='nearest', origin='lower', cmap=cmap)
    plt.title(f"{system} Secondary Structure Timeline")
    plt.xlabel("Frame")
    plt.ylabel("Residue Index")

    ss_names = ['Coil', 'Alpha Helix', 'Beta Sheet', 'Turn', 'Bend', '3-10 Helix', 'Beta Bridge', 'Pi Helix', 'Polyproline II']
    patches = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors_list[v], label=ss_names[v], markersize=10)
        for v in unique_vals
    ]
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    plt.tight_layout()
    plt.savefig(f"{fig_dir}/{system}_DSSP.png", dpi=300)
    plt.close()

# Plot DCCM heatmap
def plot_dccm_heatmap(dccm_file, system, fig_dir):
    if not os.path.exists(dccm_file):
        return
    try:
        dccm = np.loadtxt(dccm_file, delimiter=',')
    except Exception as e:
        print(f"Failed to load DCCM matrix: {e}")
        return
    plt.figure(figsize=(8, 7))
    im = plt.imshow(dccm, cmap='seismic', vmin=-1.0, vmax=1.0, origin='lower')
    plt.title(f"{system} Dynamic Cross-Correlation Matrix (DCCM)")
    plt.xlabel("Residue Index")
    plt.ylabel("Residue Index")
    plt.colorbar(im, label="Cross-Correlation Coefficient")
    plt.tight_layout()
    plt.savefig(f"{fig_dir}/{system}_DCCM.png", dpi=300)
    plt.close()

# Individual Basic Plots
for system in systems:
    sys_dir = os.path.join(OUTPUT_DIR, system)

    # RMSD
    rmsd_file = os.path.join(sys_dir, "rmsd", "rmsd.xvg")
    if os.path.exists(rmsd_file):
        data = read_xvg(rmsd_file)
        if len(data) > 0:
            plt.figure(figsize=(7, 5))
            plt.plot(data[:,0], data[:,1], color="#1f77b4", linewidth=1.5)
            plt.title(f"{system} RMSD")
            plt.xlabel("Time (ps)")
            plt.ylabel("RMSD (nm)")
            plt.grid(True, linestyle="--", alpha=0.5)
            plt.tight_layout()
            plt.savefig(f"{FIG_DIR}/{system}_RMSD.png", dpi=300)
            plt.close()

    # RMSF
    rmsf_file = os.path.join(sys_dir, "rmsf", "rmsf.xvg")
    if os.path.exists(rmsf_file):
        data = read_xvg(rmsf_file)
        if len(data) > 0:
            plt.figure(figsize=(7, 5))
            plt.plot(data[:,0], data[:,1], color="#2ca02c", linewidth=1.5)
            plt.title(f"{system} RMSF")
            plt.xlabel("Residue")
            plt.ylabel("RMSF (nm)")
            plt.grid(True, linestyle="--", alpha=0.5)
            plt.tight_layout()
            plt.savefig(f"{FIG_DIR}/{system}_RMSF.png", dpi=300)
            plt.close()

    # SASA
    sasa_file = os.path.join(sys_dir, "sasa", "sasa.xvg")
    if os.path.exists(sasa_file):
        data = read_xvg(sasa_file)
        if len(data) > 0:
            plt.figure(figsize=(7, 5))
            plt.plot(data[:,0], data[:,1], color="#d62728", linewidth=1.5)
            plt.title(f"{system} SASA")
            plt.xlabel("Time (ps)")
            plt.ylabel("SASA (nm²)")
            plt.grid(True, linestyle="--", alpha=0.5)
            plt.tight_layout()
            plt.savefig(f"{FIG_DIR}/{system}_SASA.png", dpi=300)
            plt.close()

    # Radius of Gyration
    rg_file = os.path.join(sys_dir, "rg", "rg.xvg")
    if os.path.exists(rg_file):
        data = read_xvg(rg_file)
        if len(data) > 0:
            plt.figure(figsize=(7, 5))
            plt.plot(data[:,0], data[:,1], color="#9467bd", linewidth=1.5)
            plt.title(f"{system} Radius of Gyration")
            plt.xlabel("Time (ps)")
            plt.ylabel("Rg (nm)")
            plt.grid(True, linestyle="--", alpha=0.5)
            plt.tight_layout()
            plt.savefig(f"{FIG_DIR}/{system}_Rg.png", dpi=300)
            plt.close()

    # Advanced calculations per system
    pca_file = os.path.join(sys_dir, "pca", "projection.xvg")
    plot_fel(pca_file, system, FIG_DIR)

    dssp_file = os.path.join(sys_dir, "dssa", "dssp.dat")
    plot_dssp_heatmap(dssp_file, system, FIG_DIR)

    dccm_file = os.path.join(sys_dir, "dccm", "dccm.csv")
    plot_dccm_heatmap(dccm_file, system, FIG_DIR)

    # 3D PCA Scatter Density Plot
    if os.path.exists(pca_file):
        pc1, pc2 = read_pca_projection(pca_file)
        if len(pc1) >= 5:
            try:
                xy = np.vstack([pc1, pc2])
                density = gaussian_kde(xy)(xy)
                fig = plt.figure(figsize=(8,6))
                ax = fig.add_subplot(111, projection="3d")
                sc = ax.scatter(pc1, pc2, density, c=density, cmap="plasma", s=10)
                ax.set_title(f"{system} PCA Conformational Space")
                ax.set_xlabel("PC1 (nm)")
                ax.set_ylabel("PC2 (nm)")
                ax.set_zlabel("Conformational Density")
                plt.colorbar(sc, label="Density")
                plt.tight_layout()
                plt.savefig(f"{FIG_DIR}/{system}_PCA.png", dpi=300)
                plt.close()
            except Exception as e:
                print(f"KDE PCA plotting failed for {system}: {e}")

# Overlay Plot Helper
def overlay_plot(metric, ylabel, subdir, filename):
    plt.figure(figsize=(8, 5.5))
    found = False
    for system in systems:
        file = os.path.join(OUTPUT_DIR, system, subdir, filename)
        if os.path.exists(file):
            data = read_xvg(file)
            if len(data) > 0:
                plt.plot(data[:,0], data[:,1], label=system, linewidth=1.5)
                found = True
    if not found:
        plt.close()
        return
    plt.xlabel("Time (ps)" if metric != "RMSF" else "Residue")
    plt.ylabel(ylabel)
    plt.title(f"{metric} Comparison Overlay")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/{metric}_overlay.png", dpi=300)
    plt.close()

# Basic Overlays
overlay_plot("RMSD", "RMSD (nm)", "rmsd", "rmsd.xvg")
overlay_plot("SASA", "SASA (nm²)", "sasa", "sasa.xvg")
overlay_plot("Rg", "Rg (nm)", "rg", "rg.xvg")

# RMSF Overlay (Special case)
plt.figure(figsize=(8, 5.5))
found = False
for system in systems:
    file = os.path.join(OUTPUT_DIR, system, "rmsf", "rmsf.xvg")
    if os.path.exists(file):
        data = read_xvg(file)
        if len(data) > 0:
            plt.plot(data[:,0], data[:,1], label=system, linewidth=1.5)
            found = True
if found:
    plt.xlabel("Residue")
    plt.ylabel("RMSF (nm)")
    plt.title("RMSF Comparison Overlay")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/RMSF_overlay.png", dpi=300)
plt.close()

# HBOND Overlay
plt.figure(figsize=(8, 5.5))
found = False
for system in systems:
    file = os.path.join(OUTPUT_DIR, system, "hbond", "hbond.xvg")
    if os.path.exists(file):
        data = read_xvg(file)
        if len(data) > 0:
            plt.plot(data[:,0], data[:,1], label=system, linewidth=1.5)
            found = True
if found:
    plt.xlabel("Time (ps)")
    plt.ylabel("Number of H-bonds")
    plt.title("Hydrogen Bond Comparison Overlay")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/HBOND_overlay.png", dpi=300)
plt.close()

print("All plots generated successfully.")
