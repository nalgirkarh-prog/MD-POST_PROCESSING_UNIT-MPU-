#!/usr/bin/env bash
set -eo pipefail

echo "======================================="
echo "     MD-POST Multi-System Pipeline"
echo "======================================="

# Detect conda sh and activate
CONDA_SH=""
for loc in "$HOME/miniconda3" "$HOME/anaconda3" "/opt/miniconda3" "/opt/anaconda3"; do
    if [ -f "$loc/etc/profile.d/conda.sh" ]; then
        CONDA_SH="$loc/etc/profile.d/conda.sh"
        break
    fi
done

if [ -n "$CONDA_SH" ]; then
    source "$CONDA_SH"
    conda activate md_pipeline || echo "⚠️ Failed to activate md_pipeline conda environment."
else
    if command -v conda &> /dev/null; then
        eval "$(conda shell.bash hook)"
        conda activate md_pipeline || echo "⚠️ Failed to activate md_pipeline."
    else
        echo "⚠️ conda not found. Running with current environment."
    fi
fi

export GMX_MAXBACKUP=-1

# Verify gmx if available
if command -v gmx &> /dev/null; then
    echo "Using GROMACS:"
    which gmx
    gmx --version | head -n 5
    echo ""
else
    echo "⚠️ GROMACS (gmx) not found in PATH."
fi

INPUT_ROOT="input"
OUTPUT_ROOT="outputs"

mkdir -p "$OUTPUT_ROOT"

# Detect systems in input/
SYSTEMS=""
if [ -d "$INPUT_ROOT" ]; then
    SYSTEMS=$(find "$INPUT_ROOT" -mindepth 1 -maxdepth 1 -type d)
fi

RUN_GROMACS=true
if [[ -z "$SYSTEMS" ]]; then
    echo "⚠️ No system folders found inside input/."

    # Check if we have pre-existing outputs to run plots/stats
    DETECTED_OUTPUT_SYSTEMS=$(find "$OUTPUT_ROOT" -mindepth 1 -maxdepth 1 -type d ! -name "statistics" ! -name "llm" ! -name "final_report" ! -name "paper")
    if [[ -n "$DETECTED_OUTPUT_SYSTEMS" ]]; then
        echo "📊 Found pre-existing or mock system data in outputs/:"
        for SYS in $DETECTED_OUTPUT_SYSTEMS; do
            echo "  - $(basename "$SYS")"
        done
        echo "Proceeding with statistics, plotting, and LLM interpretation stages..."
        RUN_GROMACS=false
    else
        echo "❌ No GROMACS trajectories in input/ and no data in outputs/. Cannot proceed."
        echo "💡 Hint: Run 'python scripts/generate_mock_data.py' to generate test data first."
        exit 1
    fi
fi

if [ "$RUN_GROMACS" = true ]; then
    echo "Detected input systems:"
    for SYS in $SYSTEMS; do
        echo "  - $(basename "$SYS")"
    done
    echo ""

    for SYSTEM in $SYSTEMS; do
        SYS=$(basename "$SYSTEM")

        echo "========================================"
        echo "Processing system: $SYS"
        echo "========================================"

        mkdir -p "$OUTPUT_ROOT/$SYS"

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
fi

# Comparative statistics
echo "========================================"
echo "Running comparative statistics"
echo "========================================"
Rscript scripts/04_statistics.R

# Plot generation
echo "========================================"
echo "Generating plots"
echo "========================================"
python scripts/05_plots.py

# Report generation
echo "========================================"
echo "Generating report"
echo "========================================"
python scripts/report_generator.py

# LLM interpretation
echo "========================================"
echo "Running LLM interpretation"
echo "========================================"
python scripts/06_llm_interpretation.py

echo ""
echo "======================================="
echo "Pipeline completed successfully."
echo "======================================="
echo ""
echo "LLM interpretation generated: outputs/llm/interpretation.txt"
echo "If satisfied, generate manuscript drafts: python scripts/07_paper_builder.py"
echo ""
