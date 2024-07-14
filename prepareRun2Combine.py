#! /bin/env python

# Python imports
import os, sys, stat, argparse, getpass, json
from math import sqrt
from collections import OrderedDict
from subprocess import check_call

# to prevent pyroot to hijack argparse we need to go around
tmpargv = sys.argv[:] 
sys.argv = []

# ROOT imports
import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True
sys.argv = tmpargv

cmssw_base = os.environ['CMSSW_BASE']
base_path = os.path.join(cmssw_base, 'src/UserCode/LFVTOPLimits')

parser = argparse.ArgumentParser(description='Create shape datacards ready for combine')

parser.add_argument('-p16pre', '--path16pre', action='store', dest='path_16pre', type=str, default='datacards_2016pre', help='Path to 2016pre datacard folder')
parser.add_argument('-p16post', '--path16post', action='store', dest='path_16post', type=str, default='datacards_2016post', help='Path to 2016post datacard folder')
parser.add_argument('-p17', '--path17', action='store', dest='path_17', type=str, default='datacards_2017', help='Path to 2017 datacard folder')
parser.add_argument('-p18', '--path18', action='store', dest='path_18', type=str, default='datacards_2018', help='Path to 2018 datacard folder')
parser.add_argument('-o', '--output', action='store', dest='output', type=str, default='fullRun2Comb', help='Output directory, please follow convention to distunguish input cards')
parser.add_argument('--nosys', action='store', dest='nosys', default=False, help='Consider or not systematic uncertainties')

options = parser.parse_args()

years = ['16pre16post1718']
signals = ['st_lfv_cs', 'st_lfv_ct', 'st_lfv_cv', 'st_lfv_us', 'st_lfv_ut', 'st_lfv_uv']
#signals = ['st_lfv_uv'] #for control plots
if cmssw_base not in options.path_16pre:
    options.path_16pre = os.path.join(base_path, options.path_16pre)
if cmssw_base not in options.path_16post:
    options.path_16post = os.path.join(base_path, options.path_16post)
if cmssw_base not in options.path_17:
    options.path_17 = os.path.join(base_path, options.path_17)
if cmssw_base not in options.path_18:
    options.path_18 = os.path.join(base_path, options.path_18)
if cmssw_base not in options.output:
    options.output = os.path.join(base_path, options.output)

try:
    os.makedirs( options.output )
    for signal in signals:
        os.makedirs( os.path.join(options.output, signal) )
except:
    print "Limit folder already exist! Overwriting contents"
    pass

for signal in signals:
    os.chdir( os.path.join(base_path, options.output, signal) )
    print(os.path.join(base_path, options.output, signal) )
    output_prefix_list = []

    for year in years:
        card_name = 'TOP_LFV_{}_Discriminant_DNN_{}.dat'.format(signal, signal)
        print("card name : " , card_name)
        command_string = 'combineCards.py'
        if '16pre' in year: command_string += ' year_2016pre=' + os.path.join(options.path_16pre, signal, card_name)
        if '16post' in year: command_string += ' year_2016post=' + os.path.join(options.path_16post, signal, card_name)
        if '17' in year: command_string += ' year_2017=' + os.path.join(options.path_17, signal, card_name)
        if '18' in year: command_string += ' year_2018=' + os.path.join(options.path_18, signal, card_name)
        command_string += ' > TOP_LFV_{}_Discriminant_DNN_{}_{}.dat'.format(signal, signal, year)
        check_call(command_string, shell=True)
        output_prefix_list.append('TOP_LFV_{}_Discriminant_DNN_{}_{}'.format(signal, signal, year))

        # Backgrounds is a list of string of the considered backgrounds corresponding to entries in processes_mapping
        # Signals is a list of string of the considered signals corresponding to entries in processes_mapping
        # discriminant is the corresponding entry in the dictionary discriminants

    print("out put prefix list :" , output_prefix_list)
    fake_mass = '125'

    # Write card
    for output_prefix in output_prefix_list:
        year = output_prefix.split('_')[10]
        if year == '16pre16post1718':
            year = 'Run2'
        output_dir = os.path.join(options.output, signal)
        datacard = os.path.join(output_dir, output_prefix + '.dat')
        workspace_file = os.path.basename( os.path.join(output_dir, output_prefix + '_combine_workspace.root') )

        r_range = '0.5'
        if 'st_lfv_us' in signal: r_range = '0.1'
        elif 'st_lfv_uv' in signal: r_range = '0.03'
        elif 'st_lfv_ut' in signal: r_range = '0.01'
        elif 'st_lfv_ct' in signal: r_range = '0.1'

        script = """#! /bin/bash

text2workspace.py {datacard} -m {fake_mass} -o {workspace_root}

# Run limit

echo combine -M AsymptoticLimits -n {name} {workspace_root} #--run blind #-v +2
combine -M AsymptoticLimits -n {name} {workspace_root} --rMin -1 --rMax 1 --rAbsAcc 0.0000005 --cminDefaultMinimizerStrategy 0  #-v +2
#combine -H AsymptoticLimits -M HybridNew -n {name} {workspace_root} --LHCmode LHC-limits --expectedFromGrid 0.5 #for ecpected, use 0.84 and 0.16

combine -M MultiDimFit {name}_combine_workspace.root -n .NLLScan --rMin -0.5 --rMax 0.5 --algo grid --points 100
python ../../plot1DScan.py higgsCombine.NLLScan.MultiDimFit.mH120.root -o single_scan_Run2_{signal}
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, fake_mass=fake_mass,  signal=signal, systematics=(0 if options.nosys else 1))
        script_file = os.path.join(output_dir, output_prefix + '_run_limits.sh')
        with open(script_file, 'w') as f:
            f.write(script)

        st = os.stat(script_file)
        os.chmod(script_file, st.st_mode | stat.S_IEXEC)

        r_range = '20'
        if 'st_lfv_us' in signal: r_range = '1'
        elif 'st_lfv_uv' in signal: r_range = '1'
        elif 'st_lfv_ut' in signal: r_range = '0.005'
        elif 'st_lfv_ct' in signal: r_range = '2'

        # Write small script for impacts
        script = """#! /bin/bash

## Run impacts
combineTool.py -M FastScan -w {name}_combine_workspace.root:w -o {name}_nll

combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --doInitialFit --robustFit=1 --rMin -{r_range} --rMax {r_range} -t -1
combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --robustFit=1 --doFits --rMin -{r_range} --rMax {r_range} -t -1 --parallel 50
combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 -o {name}_expected_impacts.json --rMin -{r_range} --rMax {r_range} -t -1
plotImpacts.py -i {name}_expected_impacts.json -o {name}_expected_impacts --per-page 50

combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --doInitialFit --robustFit=1 --rMin -{r_range} --rMax {r_range}
combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --robustFit=1 --doFits --rMin -{r_range} --rMax {r_range} --parallel 50
combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 -o {name}_impacts.json --rMin -{r_range} --rMax {r_range}
plotImpacts.py -i {name}_impacts.json -o {name}_impacts --per-page 50
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, fake_mass=fake_mass, r_range=r_range, systematics=(0 if options.nosys else 1))
        script_file = os.path.join(output_dir, output_prefix + '_run_impacts.sh')
        with open(script_file, 'w') as f:
            f.write(script)

        st = os.stat(script_file)
        os.chmod(script_file, st.st_mode | stat.S_IEXEC)

        # Write small script for postfit shapes
        script = """#! /bin/bash

# Run postfit
echo combine -M FitDiagnostics {datacard} -n _{name}_postfit --saveNormalizations --saveShapes --saveWithUncertainties --preFitValue 0 --rMin -{r_range} --rMax {r_range} --robustFit=1 -v 1
combine -M FitDiagnostics {datacard} -n _{name}_postfit --saveNormalizations --saveShapes --saveWithUncertainties --preFitValue 0 --rMin -{r_range} --rMax {r_range} --robustFit=1 -m {fake_mass} -v 1 #--plots
PostFitShapesFromWorkspace -w {name}_combine_workspace.root -d {datacard} -o postfit_shapes_{name}.root -f fitDiagnostics_{name}_postfit.root:fit_b --postfit --sampling -m {fake_mass}
python ../../convertPostfitShapesForPlotIt.py -i postfit_shapes_{name}.root
python ../../merge_postfits.py
../../plotIt/plotIt -o postfit_shapes_TOP_LFV_forPlotIt ../../plotIt/configs/TOP-22-011/postfit_config_Run2.yml -y --allSig --selectSig {coupling}
cd postfit_shapes_TOP_LFV_forPlotIt
mv DNN_logx_logy.pdf DNN_{coupling}_{year}_logx_logy.pdf
mv DNN_logx_logy.png DNN_{coupling}_{year}_logx_logy.png
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, fake_mass=fake_mass, r_range=r_range, systematics=(0 if options.nosys else 1), coupling=signal, year=year)
        script_file = os.path.join(output_dir, output_prefix + '_run_postfit.sh')
        with open(script_file, 'w') as f:
            f.write(script)

        st = os.stat(script_file)
        os.chmod(script_file, st.st_mode | stat.S_IEXEC)

        # Write small script for goodness of fit
        script = """#! /bin/bash

# Run GoodnessOfFit
echo combine -M GoodnessOfFit --algo=saturated -d {workspace_root} -n _{name}_toys --cminDefaultMinimizerStrategy 0 --fixedSignalStrength=0 -t 500
combine -M GoodnessOfFit --algo=saturated -d {workspace_root} -n _{name}_data --cminDefaultMinimizerStrategy 0 --fixedSignalStrength=0 > GOF_log
combine -M GoodnessOfFit --algo=saturated -d {workspace_root} -n _{name}_toys --cminDefaultMinimizerStrategy 0 --fixedSignalStrength=0 -t 500 >> GOF_log
python ../../GOF_plotPValue.py -t higgsCombine_{name}_toys.GoodnessOfFit.mH120.123456.root -d higgsCombine_{name}_data.GoodnessOfFit.mH120.root -o GOF_{coupling}_{year}
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, fake_mass=fake_mass, r_range=r_range, systematics=(0 if options.nosys else 1), coupling=signal, year=year)
        script_file = os.path.join(output_dir, output_prefix + '_run_gof.sh')
        with open(script_file, 'w') as f:
            f.write(script)

        st = os.stat(script_file)
        os.chmod(script_file, st.st_mode | stat.S_IEXEC)


os.chdir( os.path.join(cmssw_base) )
