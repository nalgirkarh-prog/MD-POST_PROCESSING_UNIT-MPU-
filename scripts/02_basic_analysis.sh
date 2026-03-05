#!/usr/bin/env bash

set -eo pipefail

SYS=$1

INPUT_DIR="input"
OUTPUT_BASE="outputs"

SYSTEM_DIR="$INPUT_DIR/$SYS"
OUTPUT_DIR="$OUTPUT_BASE/$SYS"

TPR=$(find "$SYSTEM_DIR" -maxdepth 1 -name "*.tpr" | head -n 1)
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

echo "RMSD..."

printf "4\n4\n" | gmx rms \
-s "$TPR" \
-f "$TRAJ" \
-o "$OUTPUT_DIR/rmsd/rmsd.xvg"

echo "RMSF..."

printf "4\n" | gmx rmsf \
-s "$TPR" \
-f "$TRAJ" \
-o "$OUTPUT_DIR/rmsf/rmsf.xvg"

echo "SASA..."

printf "1\n" | gmx sasa \
-s "$TPR" \
-f "$TRAJ" \
-o "$OUTPUT_DIR/sasa/sasa.xvg"

echo "H-bonds..."

printf "1\n12\n" | gmx hbond \
-s "$TPR" \
-f "$TRAJ" \
-num "$OUTPUT_DIR/hbond/hbond.xvg"

echo "Radius of Gyration..."

printf "1\n" | gmx gyrate \
-s "$TPR" \
-f "$TRAJ" \
-o "$OUTPUT_DIR/rg/rg.xvg"

echo "Basic analysis complete for $SYS"
