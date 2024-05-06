datacardFolder=$1
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -limitfolder $datacardFolder
python printLimitLatexTable.py $datacardFolder > out_${datacardFolder}.tex
python run_all_impacts.py $datacardFolder
python plot_syst.py $datacardFolder
python run_all_gatherFailedFits.py $datacardFolder

#python run_all_postfits.py $datacardFolder
#python printPostfitLatexTable.py $datacardFolder
#python get_postfit_scale.py $datacardFolder
