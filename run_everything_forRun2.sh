postfix=$1
datacardFolder=fullRun2Comb_$postfix
python prepareRun2Combine.py -o $datacardFolder \
    -p16pre  datacards_2016pre_${postfix} \
    -p16post datacards_2016post_${postfix} \
    -p17     datacards_2017_${postfix} \
    -p18     datacards_2018_${postfix}
python run_all_limits.py $datacardFolder
python plotLimitsPerCategory.py -limitfolder $datacardFolder
python printLimitLatexTable.py $datacardFolder > out_$datacardFolder
python run_all_impacts.py $datacardFolder
python run_all_gatherFailedFits.py $datacardFolder

#python run_all_postfits.py $datacardFolder
#python printPostfitLatexTable.py $datacardFolder
#python plotLimitsInterpolation.py -limitfolder $datacardFolder
