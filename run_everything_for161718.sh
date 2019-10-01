source combineCards.sh datacards_190702_2016_norebin/ datacards_190702_2017/ datacards_190702_2018/
python run_all_limits.py fullComb
python plotLimitsPerCategory.py -limitfolder fullComb -removeHutb4j4 False -lumi 137.2 -doPlot False #Need this to write json file for 'all' category
