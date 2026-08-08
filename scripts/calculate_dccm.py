import os
import argparse
import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis import align

def main():
    parser = argparse.ArgumentParser(description="Calculate DCCM using MDAnalysis")
    parser.add_argument("-s", "--tpr", required=True, help="Input TPR topology file")
    parser.add_argument("-f", "--trajectory", required=True, help="Input XTC trajectory file")
    parser.add_argument("-o", "--output", required=True, help="Output path for DCCM data (CSV format)")
    args = parser.parse_args()

    print(f"Loading topology: {args.tpr} and trajectory: {args.trajectory}")
    u = mda.Universe(args.tpr, args.trajectory)

    # Align trajectory on CA atoms to remove global rotation and translation
    print("Aligning trajectory on C-alpha atoms...")
    aligner = align.AlignTraj(u, u, select="name CA", in_memory=True)
    aligner.run()

    # Select CA atoms
    ca_atoms = u.select_atoms("name CA")
    n_atoms = len(ca_atoms)
    n_frames = len(u.trajectory)
    print(f"Number of C-alpha atoms: {n_atoms}")
    print(f"Number of frames: {n_frames}")

    if n_atoms == 0 or n_frames == 0:
        raise ValueError("No C-alpha atoms found or trajectory is empty.")

    # Get positions for all frames
    # Shape: (n_frames, n_atoms, 3)
    positions = np.zeros((n_frames, n_atoms, 3))
    for i, ts in enumerate(u.trajectory):
        positions[i] = ca_atoms.positions

    # Subtract average position of each atom
    mean_positions = np.mean(positions, axis=0) # shape: (n_atoms, 3)
    displacements = positions - mean_positions # shape: (n_frames, n_atoms, 3)

    # Calculate covariance: C_ij = <d_i . d_j>
    # Using np.einsum for efficient calculation
    print("Computing covariance matrix...")
    cov = np.einsum("tik,tjk->ij", displacements, displacements) / n_frames

    # Compute cross-correlation: C_ij / sqrt(C_ii * C_jj)
    print("Computing DCCM matrix...")
    variance = np.diag(cov)
    std_dev = np.sqrt(variance)
    # Avoid division by zero
    std_dev[std_dev == 0] = 1.0

    dccm = cov / np.outer(std_dev, std_dev)

    # Ensure values are strictly between -1 and 1
    dccm = np.clip(dccm, -1.0, 1.0)

    # Save DCCM to CSV
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    np.savetxt(args.output, dccm, delimiter=",", fmt="%.6f")
    print(f"Saved DCCM matrix to {args.output}")

if __name__ == "__main__":
    main()
