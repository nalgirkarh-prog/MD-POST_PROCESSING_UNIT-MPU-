#!/bin/bash

# Auto-detect input files based on extension
TPR=$(ls input/*.tpr 2>/dev/null | head -n1)
XTC=$(ls input/*.xtc 2>/dev/null | head -n1)
GRO=$(ls input/*.gro 2>/dev/null | head -n1)
TOP=$(ls input/*.top 2>/dev/null | head -n1)
NDX=$(ls input/*.ndx 2>/dev/null | head -n1)

if [[ -z "$TPR" || -z "$XTC" ]]; then
    echo "❌ Missing required .tpr or .xtc files in input/"
    exit 1
fi

echo "Detected:"
echo "TPR: $TPR"
echo "XTC: $XTC"
echo "GRO: $GRO"
echo "TOP: $TOP"
echo "NDX: $NDX"
