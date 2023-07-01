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

parser = argparse.ArgumentParser(description='Create shape datacards ready for combine')

parser.add_argument('-p16pre', '--path16pre', action='store', dest='path_16pre', type=str, default=cmssw_base+'/src/UserCode/FCNCLimits/datacards_top_lfv_multiClass_June2023_GoingtoPrep_2_2016pre', help='Directory containing data cards of 2016 analysis')
parser.add_argument('-p16post', '--path16post', action='store', dest='path_16post', type=str, default=cmssw_base+'/src/UserCode/FCNCLimits/datacards_top_lfv_multiClass_June2023_GoingtoPrep_2_2016post', help='Directory containing data cards of 2016 analysis')
parser.add_argument('-p17', '--path17', action='store', dest='path_17', type=str, default=cmssw_base+'/src/UserCode/FCNCLimits/datacards_top_lfv_multiClass_June2023_GoingtoPrep_2_2017', help='Directory containing data cards of 2017 analysis')
parser.add_argument('-p18', '--path18', action='store', dest='path_18', type=str, default=cmssw_base+'/src/UserCode/FCNCLimits/datacards_top_lfv_multiClass_June2023_GoingtoPrep_2_2018', help='Directory containing data cards of 2018 analysis')
parser.add_argument('-o', '--output', action='store', dest='output', type=str, default='fullComb_default', help='Output directory, please follow convention to distunguish input cards') 
parser.add_argument('--nosys', action='store', dest='nosys', default=False, help='Consider or not systematic uncertainties (NB : bbb uncertainty is with another flag)')

options = parser.parse_args()

years = ['16pre16post1718']

if cmssw_base not in options.path_16pre:
  options.path_16pre = os.path.join(cmssw_base, 'src/UserCode/FCNCLimits/', options.path_16pre)
if cmssw_base not in options.path_16post:
  options.path_16post = os.path.join(cmssw_base, 'src/UserCode/FCNCLimits/', options.path_16post)
if cmssw_base not in options.path_17:
  options.path_17 = os.path.join(cmssw_base, 'src/UserCode/FCNCLimits/', options.path_17)
if cmssw_base not in options.path_18:
  options.path_18 = os.path.join(cmssw_base, 'src/UserCode/FCNCLimits/', options.path_18)
if cmssw_base not in options.output:
  options.output = os.path.join(cmssw_base, 'src/UserCode/FCNCLimits/', options.output)

try:
  os.makedirs( options.output )
  for signal in ['st_lfv_cs','st_lfv_ct','st_lfv_cv','st_lfv_us','st_lfv_ut','st_lfv_uv']:
    os.makedirs( os.path.join(options.output, signal) )
except:
  print "Limit folder already exist! Overwriting contents"
  pass

for signal in ['st_lfv_cs','st_lfv_ct','st_lfv_cv','st_lfv_us','st_lfv_ut','st_lfv_uv']:
  os.chdir( os.path.join(cmssw_base, 'src/UserCode/FCNCLimits/', options.output, signal) )
  print(os.path.join(cmssw_base, 'src/UserCode/FCNCLimits/', options.output, signal) )
  output_prefix_list = []

  for year in years:
    card_name = 'FCNC_{}_Discriminant_DNN_{}.dat'.format(signal, signal)
    print("card name : " , card_name)
    command_string = 'combineCards.py'
    if '16pre' in year: command_string += ' year_2016pre=' + os.path.join(options.path_16pre, signal, card_name)
    if '16post' in year: command_string += ' year_2016post=' + os.path.join(options.path_16post, signal, card_name)
    if '17' in year: command_string += ' year_2017=' + os.path.join(options.path_17, signal, card_name)
    if '18' in year: command_string += ' year_2018=' + os.path.join(options.path_18, signal, card_name)
    command_string += ' > FCNC_{}_Discriminant_DNN_{}_{}.dat'.format(signal, signal, year)
    check_call(command_string, shell=True)
    output_prefix_list.append('FCNC_{}_Discriminant_DNN_{}_{}'.format(signal, signal, year))
  
    # Backgrounds is a list of string of the considered backgrounds corresponding to entries in processes_mapping
    # Signals is a list of string of the considered signals corresponding to entries in processes_mapping
    # discriminant is the corresponding entry in the dictionary discriminants

  print("out put prefix list :" , output_prefix_list) 
  fake_mass = '125'

  # Write card
  for output_prefix in output_prefix_list:
    year = output_prefix.split('_')[9]
    output_dir = os.path.join(options.output, signal)
    datacard = os.path.join(output_dir, output_prefix + '.dat')
    workspace_file = os.path.basename( os.path.join(output_dir, output_prefix + '_combine_workspace.root') )
    script = """#! /bin/bash

text2workspace.py {datacard} -m {fake_mass} -o {workspace_root}

# Run limit

echo combine -M AsymptoticLimits -n {name} {workspace_root} --run blind #-v +2
#combine -M AsymptoticLimits -n {name} {workspace_root} #--run expected #-v +2
combine -M AsymptoticLimits -n {name} {workspace_root} --run blind  --rMin -1 --rMax 1 --rAbsAcc 0.0000005 --expectSignal 1 --cminDefaultMinimizerStrategy 0  #-v +2
#combine -H AsymptoticLimits -M HybridNew -n {name} {workspace_root} --LHCmode LHC-limits --expectedFromGrid 0.5 #for ecpected, use 0.84 and 0.16
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, fake_mass=fake_mass, systematics=(0 if options.nosys else 1))
    script_file = os.path.join(output_dir, output_prefix + '_run_limits.sh')
    with open(script_file, 'w') as f:
        f.write(script)
    
    st = os.stat(script_file)
    os.chmod(script_file, st.st_mode | stat.S_IEXEC)

    # Write small script for datacard checks
    script = """#! /bin/bash

# Run checks
echo combine -M FitDiagnostics -t -1 --expectSignal 0 {datacard} -n fitDiagnostics_{name}_bkgOnly -m 125 --robustHesse 1 --robustFit=1 --rMin -20 --rMax 20 #--plots
echo python ../../../../HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a fitDiagnostics_{name}_bkgOnly.root -g fitDiagnostics_{name}_bkgOnly_plots.root
combine -M FitDiagnostics -t -1 --expectSignal 0 {datacard} -n _{name}_bkgOnly -m 125 --robustHesse 1 --robustFit=1 --rMin -20 --rMax 20 #--plots
python ../../../../HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a fitDiagnostics_{name}_bkgOnly.root -g fitDiagnostics_{name}_bkgOnly_plots.root --skipFitS --skipBBB > fitDiagnostics_{name}_bkgOnly.log
python ../../printPulls.py fitDiagnostics_{name}_bkgOnly_plots.root
combine -M FitDiagnostics -t -1 --expectSignal 1 {datacard} -n _{name}_bkgPlusSig -m 125 --robustHesse 1 --robustFit=1 --rMin -20 --rMax 20 #--plots
python ../../../../HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a fitDiagnostics_{name}_bkgPlusSig.root -g fitDiagnostics_{name}_bkgPlusSig_plots.root --skipFitB --skipBBB > fitDiagnostics_{name}_bkgPlusSig.log
python ../../printPulls.py fitDiagnostics_{name}_bkgPlusSig_plots.root

#print NLL for check
combineTool.py -M FastScan -w {name}_combine_workspace.root:w -o {name}_nll
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, fake_mass=fake_mass, systematics=(0 if options.nosys else 1))
    script_file = os.path.join(output_dir, output_prefix + '_run_closureChecks.sh')
    with open(script_file, 'w') as f:
        f.write(script)
    
    st = os.stat(script_file)
    os.chmod(script_file, st.st_mode | stat.S_IEXEC)

    # Write small script for impacts
    script = """#! /bin/bash

## Run impacts
combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --doInitialFit --robustFit=1 --robustHesse 1 --rMin -20 --rMax 20 -t -1
combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --robustFit=1 --robustHesse 1 --doFits --rMin -20 --rMax 20 -t -1 --parallel 32
combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 -o {name}_expected_impacts.json --rMin -20 --rMax 20 -t -1
plotImpacts.py -i {name}_expected_impacts.json -o {name}_expected_impacts --per-page 50

#combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --doInitialFit --robustFit=1 --robustHesse 1 --rMin -20 --rMax 20
#combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --robustFit=1 --doFits --robustHesse 1 --rMin -20 --rMax 20 --parallel 32
#combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 -o {name}_impacts.json --rMin -20 --rMax 20
#plotImpacts.py -i {name}_impacts.json -o {name}_impacts --per-page 50
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, fake_mass=fake_mass, systematics=(0 if options.nosys else 1))
    script_file = os.path.join(output_dir, output_prefix + '_run_impacts.sh')
    with open(script_file, 'w') as f:
        f.write(script)
      
    st = os.stat(script_file)
    os.chmod(script_file, st.st_mode | stat.S_IEXEC)

    # Write small script for postfit shapes
    script = """#! /bin/bash

# Run postfit
echo combine -M FitDiagnostics {datacard} -n _{name}_postfit --saveNormalizations --saveShapes --saveWithUncertainties --preFitValue 0 --rMin -20 --rMax 20 --robustHesse 1 --robustFit=1 -v 1
combine -M FitDiagnostics {datacard} -n _{name}_postfit --saveNormalizations --saveShapes --saveWithUncertainties --preFitValue 0 --rMin -20 --rMax 20 --robustHesse 1 --robustFit=1 -m {fake_mass} -v 1 #--plots
PostFitShapesFromWorkspace -w {name}_combine_workspace.root -d {datacard} -o postfit_shapes_{name}.root -f fitDiagnostics_{name}_postfit.root:fit_b --postfit --sampling -m {fake_mass}
python ../../convertPostfitShapesForPlotIt.py -i postfit_shapes_{name}.root
python ../../merge_postfits.py {coupling} {year}
$CMSSW_BASE/src/UserCode/HEPToolsFCNC/plotIt/plotIt -o postfit_shapes_{name}_forPlotIt ../../postfit_plotIt_config_{coupling}_{year}.yml -y
$CMSSW_BASE/src/UserCode/HEPToolsFCNC/plotIt/plotIt -o postfit_shapes_{name}_forPlotIt ../../postfit_plotIt_config_{coupling}_{year}_qcd.yml -y
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, fake_mass=fake_mass, systematics=(0 if options.nosys else 1), coupling=signal, year=year)
    script_file = os.path.join(output_dir, output_prefix + '_run_postfit.sh')
    with open(script_file, 'w') as f:
        f.write(script)

    st = os.stat(script_file)
    os.chmod(script_file, st.st_mode | stat.S_IEXEC)


os.chdir( os.path.join(cmssw_base) )
