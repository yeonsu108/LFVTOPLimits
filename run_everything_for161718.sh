datacardFolder=$1
python prepareRun2Combine.py -p16 datacards_190702_2016_norebin_systDef/ -p17 datacards_190702_2017/ -p18 datacards_190702_2018/ -o $datacardFolder
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -limitfolder $datacardFolder -removeHutb4j4 False -lumi 137.2  #Need this to write json file for 'all' category
#python printLimitLatexTable.py $datacardFolder False
