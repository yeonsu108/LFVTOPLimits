datacardFolder=$1 
#python prepareShapesAndCards.py -o $datacardFolder -p histos_suitable_for_limits_201215v6_2017/training_0102010203/ -xsecfile xsec_2017_200101_allComb.yml
python prepareShapesAndCards.py -o $datacardFolder -p histos_suitable_for_limits_201215v6_2017/training_0102010203/
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -limitfolder $datacardFolder 
python printLimitLatexTable.py $datacardFolder False unblind
python run_all_closureChecks.py $datacardFolder
python run_all_impacts.py $datacardFolder
python run_all_gatherFailedFits.py $datacardFolder
python run_all_postfits.py $datacardFolder
python printPostfitLatexTable.py $datacardFolder
python get_postfit_scale.py $datacardFolder
