folder=$1 
python run_all_limits.py $folder
python run_all_closureChecks.py $folder
python run_all_impacts.py $folder
python run_all_postfits.py $folder
python plotLimitsPerCategory.py -limitfolder $folder
