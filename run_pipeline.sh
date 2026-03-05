#!/usr/bin/env bash
set -eo pipefail

echo "======================================="
echo "     MD-POST Multi-System Pipeline"
echo "======================================="

########################################
# Activate Conda Environment
########################################

source ~/miniconda3/etc/profile.d/conda.sh
conda activate md_pipeline

export GMX_MAXBACKUP=-1

echo ""
echo "Using GROMACS:"
which gmx
gmx --version
echo ""

########################################
# Define directories
########################################

INPUT_ROOT="input"
OUTPUT_ROOT="outputs"

mkdir -p "$OUTPUT_ROOT"

########################################
# Detect systems
########################################

SYSTEMS=$(find "$INPUT_ROOT" -mindepth 1 -maxdepth 1 -type d)

if [[ -z "$SYSTEMS" ]]; then
    echo "❌ No system folders found inside input/"
    exit 1
fi

echo "Detected systems:"
for SYS in $SYSTEMS; do
    echo "  - $(basename "$SYS")"
done
echo ""

########################################
# Run pipeline per system
########################################

for SYSTEM in $SYSTEMS; do

    SYS=$(basename "$SYSTEM")

    echo "================================"
    echo "Processing system: $SYS"
    echo "================================"

    mkdir -p "$OUTPUT_ROOT/$SYS"

    ################################
    # Preprocessing
    ################################

echo "Stage 1: Preprocessing"
if ! bash scripts/01_preprocess.sh "$SYS"; then
    echo "❌ Preprocessing failed for $SYS — skipping system"
    continue
fi

echo "Stage 2: Basic analysis"
if ! bash scripts/02_basic_analysis.sh "$SYS"; then
    echo "❌ Basic analysis failed for $SYS — skipping system"
    continue
fi

echo "Stage 3: Advanced analysis"
if ! bash scripts/03_advanced_analysis.sh "$SYS"; then
    echo "❌ Advanced analysis failed for $SYS — skipping system"
    continue
fi
done

########################################
# Cross-system statistics
########################################

echo "================================"
echo "Running comparative statistics"
echo "================================"

Rscript scripts/04_statistics.R

########################################
# Plot generation
########################################

echo "================================"
echo "Generating plots"
echo "================================"

python scripts/05_plots.py

########################################
# Report generation
########################################

echo "================================"
echo "Generating report"
echo "================================"

python scripts/report_generator.py

########################################
# LLM interpretation
########################################

echo "================================"
echo "Running LLM interpretation"
echo "================================"

python scripts/06_llm_interpretation.py

echo ""
echo "======================================="
echo "Pipeline completed successfully."
echo "======================================="

echo ""
echo "LLM interpretation generated:"
echo "outputs/llm/interpretation.txt"
echo ""

echo "If satisfied, generate manuscript drafts:"
echo ""
echo "python scripts/07_paper_builder.py"
echo ""
