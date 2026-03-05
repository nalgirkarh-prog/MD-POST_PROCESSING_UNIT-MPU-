#!/bin/bash

echo "Cleaning MD-POST workspace..."

rm -rf outputs/*
rm -rf figures/*
rm -rf scripts/outputs/*

rm -f average.pdb covar.log prob.xpm entropy.xpm enthalpy.xpm shamlog.log ener.xvg

echo "Workspace reset complete."
