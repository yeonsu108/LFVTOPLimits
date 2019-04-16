datacardFolder=$1 
python prepareShapesAndCards.py -p ../../../../rootfiles_for_limits/histos_suitable_for_limits_190410_2018/ -dataYear 2018 -l 59741 -le 1.025 -xsecfile xsec_2018_190410.yml -o $datacardFolder  
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -limitfolder $datacardFolder -lumi 59.7
python printLimitLatexTable.py $datacardFolder
python run_all_closureChecks.py $datacardFolder
python run_all_impacts.py $datacardFolder
python run_all_postfits.py $datacardFolder
