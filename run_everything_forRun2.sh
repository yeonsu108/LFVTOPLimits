datacardFolder=$1
#python prepareRun2Combine.py -o $datacardFolder
python prepareRun2Combine.py -o $datacardFolder -p16 datacards_200101_2016_nobbb -p17 datacards_200101_2017_nobbb -p18 datacards_200101_2018_nobbb
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -limitfolder $datacardFolder -removeHutb4j4 False -lumi 137.2 -printlimits True
##python plotLimitsPerCategory.py -limitfolder $datacardFolder -removeHutb4j4 True -lumi 137.2  -printlimits True
##python printLimitLatexTable.py $datacardFolder False #Currently doing it by hand due to formatting
#python run_all_closureChecks.py $datacardFolder
#python run_all_impacts.py $datacardFolder
##python run_all_postfits.py $datacardFolder
