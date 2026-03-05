import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

OUTPUT_DIR = "outputs"
FIG_DIR = "figures"

os.makedirs(FIG_DIR, exist_ok=True)

systems = [
    d for d in os.listdir(OUTPUT_DIR)
    if os.path.isdir(os.path.join(OUTPUT_DIR, d))
    and d not in ["statistics", "llm", "final_report", "paper"]
]

print("Detected systems:", systems)


################################
# XVG READER
################################

def read_xvg(file):
    data = []
    with open(file) as f:
        for line in f:
            if line.startswith(("#", "@")):
                continue
            parts = line.split()
            if len(parts) >= 2:
                data.append([float(parts[0]), float(parts[1])])
    return np.array(data)


################################
# PCA READER
################################

def read_pca_projection(file):
    pc1 = []
    pc2 = []

    with open(file) as f:
        for line in f:
            if line.startswith(("#", "@")):
                continue

            parts = line.split()
            if len(parts) >= 2:
                pc1.append(float(parts[0]))
                pc2.append(float(parts[1]))

    return np.array(pc1), np.array(pc2)


################################
# FEL XPM READER
################################

def read_xpm(file):

    matrix = []

    with open(file) as f:
        for line in f:

            line = line.strip()

            # real matrix rows start with quotes
            if line.startswith('"') and line.endswith('",'):

                row = line.strip('",')

                values = [ord(c) for c in row]

                matrix.append(values)

    # ensure rectangular matrix
    min_len = min(len(r) for r in matrix)
    matrix = [r[:min_len] for r in matrix]

    return np.array(matrix)

################################
# BASIC PLOTS
################################

for system in systems:

    sys_dir = os.path.join(OUTPUT_DIR, system)

    # RMSD
    rmsd_file = os.path.join(sys_dir, "rmsd", "rmsd.xvg")
    if os.path.exists(rmsd_file):

        data = read_xvg(rmsd_file)

        plt.figure()
        plt.plot(data[:,0], data[:,1])
        plt.title(f"{system} RMSD")
        plt.xlabel("Time (ps)")
        plt.ylabel("RMSD (nm)")
        plt.savefig(f"{FIG_DIR}/{system}_RMSD.png")
        plt.close()


    # RMSF
    rmsf_file = os.path.join(sys_dir, "rmsf", "rmsf.xvg")
    if os.path.exists(rmsf_file):

        data = read_xvg(rmsf_file)

        plt.figure()
        plt.plot(data[:,0], data[:,1])
        plt.title(f"{system} RMSF")
        plt.xlabel("Residue")
        plt.ylabel("RMSF (nm)")
        plt.savefig(f"{FIG_DIR}/{system}_RMSF.png")
        plt.close()


    # SASA
    sasa_file = os.path.join(sys_dir, "sasa", "sasa.xvg")
    if os.path.exists(sasa_file):

        data = read_xvg(sasa_file)

        plt.figure()
        plt.plot(data[:,0], data[:,1])
        plt.title(f"{system} SASA")
        plt.xlabel("Time (ps)")
        plt.ylabel("SASA (nm²)")
        plt.savefig(f"{FIG_DIR}/{system}_SASA.png")
        plt.close()


    # Radius of gyration
    rg_file = os.path.join(sys_dir, "rg", "rg.xvg")
    if os.path.exists(rg_file):

        data = read_xvg(rg_file)

        plt.figure()
        plt.plot(data[:,0], data[:,1])
        plt.title(f"{system} Radius of Gyration")
        plt.xlabel("Time (ps)")
        plt.ylabel("Rg (nm)")
        plt.savefig(f"{FIG_DIR}/{system}_Rg.png")
        plt.close()


################################
# PCA 3D SCATTER
################################

for system in systems:

    pca_file = os.path.join(OUTPUT_DIR, system, "pca", "projection.xvg")

    if os.path.exists(pca_file):

        pc1, pc2 = read_pca_projection(pca_file)

        if len(pc1) < 5:
            continue

        xy = np.vstack([pc1, pc2])
        density = gaussian_kde(xy)(xy)

        fig = plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111, projection="3d")

        sc = ax.scatter(
            pc1,
            pc2,
            density,
            c=density,
            cmap="plasma",
            s=10
        )

        ax.set_title(f"{system} PCA")

        ax.set_xlabel("PC1 (nm)")
        ax.set_ylabel("PC2 (nm)")
        ax.set_zlabel("Conformational Density")

        plt.colorbar(sc, label="Conformational Density")

        plt.tight_layout()

        plt.savefig(f"{FIG_DIR}/{system}_PCA.png", dpi=300)

        plt.close()
################################
# FEL 3D ENERGY SURFACE
################################

for system in systems:

    fel_file = os.path.join(OUTPUT_DIR, system, "fel", "fel.xpm")

    if os.path.exists(fel_file):

        matrix = read_xpm(fel_file)

        if matrix.size == 0:
            continue

        energy = matrix - matrix.min()

        x = np.arange(energy.shape[1])
        y = np.arange(energy.shape[0])

        X, Y = np.meshgrid(x, y)

        fig = plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111, projection="3d")

        surf = ax.plot_surface(
            X,
            Y,
            energy,
            cmap="jet",
            linewidth=0,
            antialiased=True
        )

        ax.contourf(
            X,
            Y,
            energy,
            zdir="z",
            offset=energy.min(),
            cmap="jet"
        )

        ax.set_zlim(energy.min(), energy.max())

        ax.set_title(f"{system} Free Energy Landscape")

        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.set_zlabel("Free Energy")

        plt.colorbar(surf, label="Free Energy")

        plt.tight_layout()

        plt.savefig(f"{FIG_DIR}/{system}_FEL.png", dpi=300)

        plt.close()
################################
# OVERLAY COMPARISON PLOTS
################################

def overlay_plot(metric, ylabel, subdir, filename):

    plt.figure(figsize=(7,5))

    found = False

    for system in systems:

        file = os.path.join(OUTPUT_DIR, system, subdir, filename)

        if os.path.exists(file):

            data = read_xvg(file)

            if len(data) == 0:
                continue

            plt.plot(
                data[:,0],
                data[:,1],
                label=system,
                linewidth=1.2
            )

            found = True

    if not found:
        plt.close()
        return

    plt.xlabel("Time (ps)" if metric != "RMSF" else "Residue")
    plt.ylabel(ylabel)

    plt.title(f"{metric} Comparison")

    plt.legend()
    plt.tight_layout()

    plt.savefig(f"{FIG_DIR}/{metric}_overlay.png", dpi=300)
    plt.close()


# RMSD overlay
overlay_plot(
    "RMSD",
    "RMSD (nm)",
    "rmsd",
    "rmsd.xvg"
)

# SASA overlay
overlay_plot(
    "SASA",
    "SASA (nm²)",
    "sasa",
    "sasa.xvg"
)

# Radius of gyration overlay
overlay_plot(
    "Rg",
    "Rg (nm)",
    "rg",
    "rg.xvg"
)


################################
# RMSF OVERLAY (special case)
################################

plt.figure(figsize=(7,5))

found = False

for system in systems:

    file = os.path.join(OUTPUT_DIR, system, "rmsf", "rmsf.xvg")

    if os.path.exists(file):

        data = read_xvg(file)

        plt.plot(
            data[:,0],
            data[:,1],
            label=system,
            linewidth=1.2
        )

        found = True

if found:

    plt.xlabel("Residue")
    plt.ylabel("RMSF (nm)")
    plt.title("RMSF Comparison")

    plt.legend()
    plt.tight_layout()

    plt.savefig(f"{FIG_DIR}/RMSF_overlay.png", dpi=300)

plt.close()


################################
# HBOND OVERLAY (optional)
################################

plt.figure(figsize=(7,5))

found = False

for system in systems:

    file = os.path.join(OUTPUT_DIR, system, "hbond", "hbond.xvg")

    if os.path.exists(file):

        data = read_xvg(file)

        plt.plot(
            data[:,0],
            data[:,1],
            label=system,
            linewidth=1.2
        )

        found = True

if found:

    plt.xlabel("Time (ps)")
    plt.ylabel("Number of H-bonds")

    plt.title("Hydrogen Bond Comparison")

    plt.legend()
    plt.tight_layout()

    plt.savefig(f"{FIG_DIR}/HBOND_overlay.png", dpi=300)

plt.close()

print("All PCA and FEL plots completed.")
