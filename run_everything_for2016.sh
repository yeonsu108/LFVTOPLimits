datacardFolder=$1 
python prepareShapesAndCards.py -p $CMSSW_BASE/src/UserCode/tHFCNC/Limit/FinalFits/suitable_for_prepareShapeAndCards/ -dataYear 2016 -l 1 -le 1.025 -xsecfile xsec_2016.yml -o $datacardFolder  
#python prepareShapesAndCards.py -o $datacardFolder -p ../../../../rootfiles_for_limits/histos_suitable_for_limits_190121_LeptonPt -rebinning 3 -dataYear 2018 -l 59741 -le 1.025 -xsecfile xsec_2018_190410.yml
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -limitfolder $datacardFolder -lumi 35.9
#python printLimitLatexTable.py $datacardFolder
#python run_all_closureChecks.py $datacardFolder
#python run_all_impacts.py $datacardFolder
#python run_all_postfits.py $datacardFolder
