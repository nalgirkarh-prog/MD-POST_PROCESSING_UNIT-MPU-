#!/usr/bin/env bash
# ============================================================
# Pipeline Configuration — loaded by analysis scripts
# ============================================================

# GROMACS selection groups (numeric index in the interactive menus)
# Group 0 = System, 1 = Protein, 3 = C-alpha, 4 = Backbone
GMX_GROUP_RMSD="4"          # Backbone vs Backbone for RMSD
GMX_GROUP_RMSF="4"          # Backbone for RMSF
GMX_GROUP_GYRATE="1"        # Protein for Rg
GMX_GROUP_SASA="1"          # Protein for SASA
GMX_GROUP_HBOND_A="1"       # Donor/acceptor group A for H-bonds
GMX_GROUP_HBOND_B="1"       # Donor/acceptor group B for H-bonds (same = intra-protein)
GMX_GROUP_PCA="3"           # C-alpha for PCA covariance
GMX_GROUP_FIT="4"           # Backbone for trajectory fitting in preprocessing

# Simulation temperature (K) — used in FEL Boltzmann inversion
SIM_TEMP=300

# Ollama model to use for LLM interpretation (set lightweight default)
# Choices: llama3.2, qwen2.5:3b, phi3, mistral
export OLLAMA_MODEL="llama3.2"

# Ollama host (for remote or containerized ollama)
export OLLAMA_HOST="http://127.0.0.1:11434"
