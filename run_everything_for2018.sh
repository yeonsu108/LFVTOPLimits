datacardFolder=$1
#python prepareShapesAndCards.py -p histos_suitable_for_limits_201215v6_2018/training_0102010203/ -dataYear 2018 -l 59741 -le 1.025 -xsecfile xsec_2018_200101_allComb.yml --sysToAvoid prefire elzvtx -o $datacardFolder #--nosys True
python prepareShapesAndCards.py -p histos_suitable_for_limits_201215v6_2018/training_0102010203/ -dataYear 2018 -l 59741 -le 1.025 -xsecfile xsec_2018_200101.yml --sysToAvoid prefire elzvtx -o $datacardFolder #--nosys True
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -lumi 59.7 -limitfolder $datacardFolder
python printLimitLatexTable.py $datacardFolder False unblind
python run_all_closureChecks.py $datacardFolder
python run_all_impacts.py $datacardFolder
python run_all_gatherFailedFits.py $datacardFolder
python run_all_postfits.py $datacardFolder
python printPostfitLatexTable.py $datacardFolder
python get_postfit_scale.py $datacardFolder
