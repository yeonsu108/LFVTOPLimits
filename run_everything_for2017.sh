datacardFolder=$1 
python prepareShapesAndCards.py -o $datacardFolder  -p histos_suitable_for_limits_200101v8_2017/training_0101010101/
#python prepareShapesAndCards.py -o $datacardFolder  -p histos_suitable_for_limits_200101v10_2017/training_0101010101/
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -limitfolder $datacardFolder
python printLimitLatexTable.py $datacardFolder False
python run_all_closureChecks.py $datacardFolder
python run_all_impacts.py $datacardFolder
python run_all_gatherFailedFits.py $datacardFolder
python run_all_postfits.py $datacardFolder
