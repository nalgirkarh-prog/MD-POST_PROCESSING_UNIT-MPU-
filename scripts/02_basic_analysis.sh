#!/usr/bin/env bash
set -eo pipefail

SYS=$1

INPUT_DIR="input"
OUTPUT_BASE="outputs"

SYSTEM_DIR="$INPUT_DIR/$SYS"
OUTPUT_DIR="$OUTPUT_BASE/$SYS"

TPR=$(find "$SYSTEM_DIR" -maxdepth 1 -name "*.tpr" | head -n 1)
NDX=$(find "$SYSTEM_DIR" -maxdepth 1 -name "*.ndx" | head -n 1)
TRAJ="$OUTPUT_DIR/processed/processed.xtc"

if [[ ! -f "$TPR" ]]; then
    echo "ERROR: No TPR file found for $SYS"
    exit 1
fi

if [[ ! -f "$TRAJ" ]]; then
    echo "ERROR: Processed trajectory missing for $SYS"
    echo "Expected: $TRAJ"
    exit 1
fi

mkdir -p "$OUTPUT_DIR/rmsd"
mkdir -p "$OUTPUT_DIR/rmsf"
mkdir -p "$OUTPUT_DIR/sasa"
mkdir -p "$OUTPUT_DIR/hbond"
mkdir -p "$OUTPUT_DIR/rg"

echo "Running basic analysis for $SYS"

if [[ -n "$NDX" ]]; then
    NDX_ARG="-n $NDX"
    echo "Using custom index file: $NDX"
else
    NDX_ARG=""
fi

echo "RMSD..."
printf "4\n4\n" | gmx rms -s "$TPR" -f "$TRAJ" $NDX_ARG -o "$OUTPUT_DIR/rmsd/rmsd.xvg"

echo "RMSF..."
printf "4\n" | gmx rmsf -s "$TPR" -f "$TRAJ" $NDX_ARG -o "$OUTPUT_DIR/rmsf/rmsf.xvg"

echo "SASA..."
printf "1\n" | gmx sasa -s "$TPR" -f "$TRAJ" $NDX_ARG -o "$OUTPUT_DIR/sasa/sasa.xvg"

echo "H-bonds (Protein-Protein)..."
# Using 1 and 1 (Protein and Protein) to guarantee success across any system
printf "1\n1\n" | gmx hbond -s "$TPR" -f "$TRAJ" $NDX_ARG -num "$OUTPUT_DIR/hbond/hbond.xvg"

echo "Radius of Gyration..."
printf "1\n" | gmx gyrate -s "$TPR" -f "$TRAJ" $NDX_ARG -o "$OUTPUT_DIR/rg/rg.xvg"

echo "Basic analysis complete for $SYS"
