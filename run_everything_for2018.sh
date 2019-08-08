datacardFolder=$1 
python prepareShapesAndCards.py -p histos_suitable_for_limits_190702_2018/training_01/ -dataYear 2018 -l 59741 -le 1.025 -xsecfile xsec_2018_190702.yml --sysToAvoid prefire -o $datacardFolder 
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -lumi 59.7 -limitfolder $datacardFolder
python printLimitLatexTable.py $datacardFolder
python run_all_closureChecks.py $datacardFolder
python run_all_impacts.py $datacardFolder
python run_all_postfits.py $datacardFolder
