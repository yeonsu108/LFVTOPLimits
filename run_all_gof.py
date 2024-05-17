import os, sys
from subprocess import call

print "Usage: python run_all_gof.py datacard_folder (optional: 1617/1718/161718)"

current_dir = os.getcwd()
datacard_path = sys.argv[1]

try:
    if any(i in sys.argv[2] for i in ['1617','1718','161718']): years = sys.argv[2]
except: years = ''

signal_folders = [folder for folder in os.listdir(datacard_path) if os.path.isdir(os.path.join(datacard_path, folder))]
if not signal_folders:
    print "Found no signal directory inside %s"%datacard_path
for signal_folder in signal_folders:
    #if "st_lfv_cs" in signal_folder or "st_lfv_ct" in signal_folder: continue
    os.chdir(os.path.join(datacard_path, signal_folder))
    gof_scripts = [gof_script for gof_script in os.listdir(".") if gof_script.endswith('_run_gof.sh')]
    if len(years) > 1:
        gof_scripts = [x for x in gof_scripts if '_'+years+'_' in x]
        limit_scripts = [limit_script for limit_script in os.listdir(".") if limit_script.endswith('_run_limits.sh')]
        limit_scripts = [x for x in limit_scripts if '_'+years+'_' in x]
        for limit_script in limit_scripts:
            print "Executing %s"%limit_script
            call(['bash', limit_script])
    if not gof_scripts:
        print "Found no limit script in directory %s"%os.path.join(datacard_path, signal_folder)
    for gof_script in gof_scripts:
        print "Executing %s"%gof_script
        call(['bash', gof_script])
    os.chdir(current_dir)
