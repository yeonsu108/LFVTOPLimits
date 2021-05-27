datacardFolder=$1
#python prepareRun2Combine.py -o $datacardFolder
#python prepareRun2Combine.py -o $datacardFolder -p16 datacards_201215_2016v1 -p17 datacards_201215_2017v3_mergeHighBins_3binsb3j3 -p18 datacards_201215_2018v3_mergeHighBins_3binsb3j3
#python prepareRun2Combine.py -o $datacardFolder -p16 datacards_201215_2016v1 -p17 datacards_201215_2017v3_mergeHighBins -p18 datacards_201215_2018v3_mergeHighBins
#python prepareRun2Combine.py -o $datacardFolder -p16 datacards_201215_2016v1 -p17 datacards_201215_2017v3 -p18 datacards_201215_2018v3
#python prepareRun2Combine.py -o $datacardFolder -p16 datacards_201215_2016v1 -p17 datacards_201215_2017v4 -p18 datacards_201215_2018v4
#python prepareRun2Combine.py -o $datacardFolder -p16 datacards_201215_2016v1 -p17 datacards_201215_2017v4_mergeHighBins -p18 datacards_201215_2018v4_mergeHighBins
python prepareRun2Combine.py -o $datacardFolder -p16 datacards_201215_2016v1 -p17 datacards_201215_2017v4_mergeb3j3HighBins -p18 datacards_201215_2018v4_mergeb3j3HighBins
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -lumi 137.2 -limitfolder $datacardFolder #For 161718  b2j3-b4j4
python printLimitLatexTable.py $datacardFolder False unblind #For 161718 b2j3-b4j4
#python run_all_closureChecks.py $datacardFolder
python run_all_impacts.py $datacardFolder
python run_all_gatherFailedFits.py $datacardFolder
python run_all_postfits.py $datacardFolder 1718
python printPostfitLatexTable.py $datacardFolder 1718
python plotLimitsInterpolation.py -limitfolder $datacardFolder

python run_all_limits.py $datacardFolder 1718
python plotLimitsPerCategory.py -lumi 137.2 -printlimits True -limitfolder $datacardFolder #For 161718, 1718, 1617
python plotLimitsInterpolation.py -category 1718_all -lumi 101.3 -limitfolder $datacardFolder
