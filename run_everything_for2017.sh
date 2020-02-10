datacardFolder=$1 
python prepareShapesAndCards.py -o $datacardFolder -removeHutb4j4 False
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -limitfolder $datacardFolder -removeHutb4j4 False
python printLimitLatexTable.py $datacardFolder False
python run_all_closureChecks.py $datacardFolder
python run_all_impacts.py $datacardFolder
python run_all_postfits.py $datacardFolder
