#!/bin/bash

datacardFolder=$1
year=$2      # e.g. v15_2024, v12_2022
channel=$3   # e.g. muon, electron

if [ -z "$datacardFolder" ] || [ -z "$year" ] || [ -z "$channel" ]; then
    echo "Usage: ./run_everything_run3.sh <datacardFolder> <year> <channel>"
    echo "Example: ./run_everything_run3.sh datacards_v15_2024_muon v15_2024 muon"
    exit 1
fi

xsecfile="../plotIt/configs/Run3_${channel}/files24.yml"

echo "Running for year: $year, channel: $channel"
echo "Output folder: $datacardFolder"
echo "Cross-section file: $xsecfile"

# Run prepareShapesAndCards.py
python prepareShapesAndCards.py -o $datacardFolder -xsecfile $xsecfile -dataYear $year -p ../DNN/DNN_0708/${channel}/${year}/

echo "Running Limits..."
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -limitfolder $datacardFolder
python printLimitLatexTable.py $datacardFolder > out_${datacardFolder}.tex
echo "Running Impacts..."
python run_all_impacts.py $datacardFolder
python plot_syst.py $datacardFolder
echo "Gathering failed fits and running postfits..."
python run_all_gatherFailedFits.py $datacardFolder
python run_all_postfits.py $datacardFolder

echo "Done!"
