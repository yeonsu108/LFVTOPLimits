datacardFolder=$1
#python prepareRun2Combine.py -o $datacardFolder
#python prepareRun2Combine.py -o $datacardFolder -p16 datacards_201215_2016v3_cor -p17 datacards_201215_2017v3_cor -p18 datacards_201215_2018v3_cor
python prepareRun2Combine.py -o $datacardFolder -p16 datacards_201215_2016v3_cor -p17 datacards_201215_2017v9_mergeHighBins_b3j3 -p18 datacards_201215_2018v9_mergeHighBins_b3j3
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -lumi 137.2 -limitfolder $datacardFolder #For 161718  b2j3-b4j4
#python plotLimitsPerCategory.py -lumi 137.2 -printlimits True -limitfolder $datacardFolder #For 161718, 1718, 1617
python printLimitLatexTable.py $datacardFolder False unblind #For 161718 b2j3-b4j4
#python printLimitLatexTable.py $datacardFolder False #For 161718, 1718, 1617
python run_all_closureChecks.py $datacardFolder
python run_all_impacts.py $datacardFolder
python run_all_gatherFailedFits.py $datacardFolder
python run_all_postfits.py $datacardFolder 1718
python printPostfitLatexTable.py $datacardFolder 1718
python plotLimitsInterpolation.py -limitfolder datacardFolder
#python plotLimitsInterpolation.py -category 1718_all -lumi 101.3 -limitfolder fullComb_201215_201215_201215v3_cor_mergeHighBins_3binsb3_for1718Interpolation
