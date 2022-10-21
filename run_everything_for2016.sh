datacardFolder=$1 
#python prepareShapesAndCards.py -p $CMSSW_BASE/src/UserCode/tHFCNC/Limit/FinalFits/suitable_for_prepareShapeAndCards_201215/ -dataYear 2016 -l 1 -le 1.025 -xsecfile xsec_2016_allComb.yml -rebinning 1 -o $datacardFolder --sysForSig [] #--sysToAvoid jec hdamp scale lepton pdf pu TuneCUETP
python prepareShapesAndCards.py -p $CMSSW_BASE/src/UserCode/tHFCNC/Limit/FinalFits/suitable_for_prepareShapeAndCards_201215/ -dataYear 2016 -l 1 -le 1.025 -xsecfile xsec_2016.yml -rebinning 1 -o $datacardFolder --sysForSig [] #--sysToAvoid jec hdamp scale lepton pdf pu TuneCUETP
##Need to change cross sections from plotLimitsPerCategory.py to reproduce numbers!##
#python prepareShapesAndCards.py -p $CMSSW_BASE/src/UserCode/tHFCNC/Limit/FinalFits/suitable_for_prepareShapeAndCards_201215/ -dataYear 2016 -l 1 -le 1.025 -xsecfile xsec_2016_TOP-17-003.yml -rebinning 1 -o $datacardFolder --sysToAvoid jec hdamp scale lepton pdf pu TuneCUETP -removeHutb4j4 True #Reproducing 2016
#python prepareShapesAndCards.py -p $CMSSW_BASE/src/UserCode/tHFCNC/Limit/FinalFits/suitable_for_prepareShapeAndCards_201215/ -dataYear 2016 -l 1 -le 1.025 -xsecfile xsec_2016.yml -rebinning 1 -o $datacardFolder --sysToAvoid jec hdamp scale lepton pdf pu TuneCUETP -removeHutb4j4 True #Reproducing 2016 but new xsec - Need to update plotLimitsPerCategory.py as well!!
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -lumi 35.9 -limitfolder $datacardFolder
python printLimitLatexTable.py $datacardFolder False unblind
#python printLimitLatexTable.py $datacardFolder True unblind #reproducing 2016
python run_all_closureChecks.py $datacardFolder
python run_all_impacts.py $datacardFolder
python run_all_gatherFailedFits.py $datacardFolder
python run_all_postfits.py $datacardFolder
python get_postfit_scale.py $datacardFolder
