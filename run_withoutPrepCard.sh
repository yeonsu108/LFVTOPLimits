datacardFolder=$1 
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -limitdatacardFolder $datacardFolder
python printLimitLatexTable.py $datacardFolder
python run_all_closureChecks.py $datacardFolder
python run_all_impacts.py $datacardFolder
python run_all_postfits.py $datacardFolder
