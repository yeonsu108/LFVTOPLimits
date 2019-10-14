datacardFolder=$1
#python prepareRun2Combine.py -p16 datacards_190702_2016_norebin_systDef/ -p17 datacards_190702_2017/ -p18 datacards_190702_2018/ -o $datacardFolder
#python prepareRun2Combine.py -p16 datacards_190702_2016_norebin_systDef_noHutb4j4/ -p17 datacards_190702_2017_noHutb4j4/ -p18 datacards_190702_2018_noHutb4j4/ -o $datacardFolder
#python prepareRun2Combine.py -p16 datacards_190702_2016_norebin_systDef_lumi/ -p17 datacards_190702_2017_lumi/ -p18 datacards_190702_2018_lumi/ -o $datacardFolder
#python prepareRun2Combine.py -p16 datacards_190702_2016_norebin_systDef_lumi/ -p17 datacards_190702_2017_lumi_ttuncor/ -p18 datacards_190702_2018_lumi_ttuncor/ -o $datacardFolder
python prepareRun2Combine.py -p16 datacards_191014_2016/ -p17 datacards_191014_2017/ -p18 datacards_191014_2018/ -o $datacardFolder
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -limitfolder $datacardFolder -removeHutb4j4 False -lumi 137.2 -printlimits True
#python plotLimitsPerCategory.py -limitfolder $datacardFolder -removeHutb4j4 True -lumi 137.2  -printlimits True
