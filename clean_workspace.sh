#!/usr/bin/env bash

echo "Cleaning MD-POST workspace..."

# Remove all outputs except .gitkeep
find outputs/ -mindepth 1 ! -name '.gitkeep' -delete 2>/dev/null || true
find figures/ -mindepth 1 ! -name '.gitkeep' -delete 2>/dev/null || true

# Remove GROMACS side-effect files that land in the project root
rm -f average.pdb covar.log prob.xpm entropy.xpm enthalpy.xpm shamlog.log ener.xvg
rm -f bindex.ndx 2>/dev/null || true

echo "Workspace reset complete."
