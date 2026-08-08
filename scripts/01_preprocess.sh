#!/usr/bin/env bash
set -eo pipefail

SYS=$1

INPUT_DIR="input"
OUTPUT_ROOT="outputs"

SYSTEM_DIR="$INPUT_DIR/$SYS"
OUTPUT_DIR="$OUTPUT_ROOT/$SYS"

mkdir -p "$OUTPUT_DIR/processed"

echo "Preprocessing $SYS"

TPR=$(find "$SYSTEM_DIR" -name "*.tpr" | head -n 1)
XTC=$(find "$SYSTEM_DIR" -name "*.xtc" | head -n 1)
NDX=$(find "$SYSTEM_DIR" -name "*.ndx" | head -n 1)

if [[ -z "$TPR" || -z "$XTC" ]]; then
    echo "ERROR: Missing trajectory files for $SYS"
    echo "TPR: $TPR"
    echo "XTC: $XTC"
    exit 1
fi

echo "TPR: $TPR"
echo "XTC: $XTC"
if [[ -n "$NDX" ]]; then
    echo "NDX: $NDX (using custom index)"
fi

echo "Removing PBC..."
if [[ -n "$NDX" ]]; then
    printf "0\n" | gmx trjconv -s "$TPR" -f "$XTC" -o "$OUTPUT_DIR/processed/nojump.xtc" -pbc nojump -n "$NDX"
else
    printf "0\n" | gmx trjconv -s "$TPR" -f "$XTC" -o "$OUTPUT_DIR/processed/nojump.xtc" -pbc nojump
fi

echo "Centering..."
if [[ -n "$NDX" ]]; then
    printf "1\n0\n" | gmx trjconv -s "$TPR" -f "$OUTPUT_DIR/processed/nojump.xtc" -o "$OUTPUT_DIR/processed/center.xtc" -center -pbc mol -n "$NDX"
else
    printf "1\n0\n" | gmx trjconv -s "$TPR" -f "$OUTPUT_DIR/processed/nojump.xtc" -o "$OUTPUT_DIR/processed/center.xtc" -center -pbc mol
fi

echo "Fitting..."
if [[ -n "$NDX" ]]; then
    printf "4\n0\n" | gmx trjconv -s "$TPR" -f "$OUTPUT_DIR/processed/center.xtc" -o "$OUTPUT_DIR/processed/processed.xtc" -fit rot+trans -n "$NDX"
else
    printf "4\n0\n" | gmx trjconv -s "$TPR" -f "$OUTPUT_DIR/processed/center.xtc" -o "$OUTPUT_DIR/processed/processed.xtc" -fit rot+trans
fi

echo "Preprocessing completed for $SYS"
