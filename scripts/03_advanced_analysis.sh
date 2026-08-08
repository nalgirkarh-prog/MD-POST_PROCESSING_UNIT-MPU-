#!/usr/bin/env bash
set -eo pipefail

SYS=$1

PROJECT_ROOT=$(pwd)
INPUT_ROOT="$PROJECT_ROOT/input"
OUTPUT_ROOT="$PROJECT_ROOT/outputs"

SYSTEM_DIR="$INPUT_ROOT/$SYS"
SYS_OUT="$OUTPUT_ROOT/$SYS"

echo "================================"
echo "Running advanced analysis for $SYS"
echo "================================"

mkdir -p "$SYS_OUT/pca"
mkdir -p "$SYS_OUT/fel"
mkdir -p "$SYS_OUT/dssa"
mkdir -p "$SYS_OUT/dccm"

# Automatically detect files
TPR=$(find "$SYSTEM_DIR" -maxdepth 1 -name "*.tpr" | head -n 1)
NDX=$(find "$SYSTEM_DIR" -maxdepth 1 -name "*.ndx" | head -n 1)
TRAJ="$SYS_OUT/processed/processed.xtc"

# Safety checks
if [[ ! -f "$TPR" ]]; then
    echo "ERROR: TPR file missing for $SYS"
    exit 1
fi

if [[ ! -f "$TRAJ" ]]; then
    echo "ERROR: Processed trajectory missing for $SYS"
    echo "Expected: $TRAJ"
    exit 1
fi

if [[ -n "$NDX" ]]; then
    NDX_ARG="-n $NDX"
    echo "Using custom index file: $NDX"
else
    NDX_ARG=""
fi

################################
# PCA
################################

echo "Running PCA..."

cd "$SYS_OUT/pca"

printf "3\n3\n" | gmx covar \
-s "$TPR" \
-f "$TRAJ" \
$NDX_ARG \
-o eigenvalues.xvg \
-v eigenvectors.trr

printf "3\n3\n" | gmx anaeig \
-v eigenvectors.trr \
-s "$TPR" \
-f "$TRAJ" \
$NDX_ARG \
-first 1 -last 2 \
-proj projection.xvg

cd "$PROJECT_ROOT"

################################
# FEL
################################

echo "FEL generation scheduled for Python plotting stage (direct Boltzmann inversion)..."

################################
# DSSP
################################

echo "Running DSSP..."

cd "$SYS_OUT/dssa"

# Using -hmode dssp for robust hydrogen-handling and outputting both .dat and stats .xvg
printf "1\n" | gmx dssp \
-s "$TPR" \
-f "$TRAJ" \
$NDX_ARG \
-hmode dssp \
-o dssp.dat \
-num dssp.xvg

cd "$PROJECT_ROOT"

################################
# DCCM
################################

echo "Generating DCCM via Python MDAnalysis..."

python "$PROJECT_ROOT/scripts/calculate_dccm.py" \
-s "$TPR" \
-f "$TRAJ" \
-o "$SYS_OUT/dccm/dccm.csv"

echo "Advanced analysis complete for $SYS"
