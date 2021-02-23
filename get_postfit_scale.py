import os, sys
from ROOT import *
import ROOT

print "Usage: python get_postfit_scale.py datacard_folder"

current_dir = os.getcwd()
datacard_path = sys.argv[1]

procs = ['ttbb', 'ttcc', 'ttlf', 'other', 'qcd']
hnames = ['DNN_SIG_b2j3','DNN_SIG_b3j3','DNN_SIG_b2j4','DNN_SIG_b3j4','DNN_SIG_b4j4']
postfit_tmp = 'postfit_shapes_FCNC_SIG_Discriminant_DNN_SIG_all.root'


signal_folders = [folder for folder in os.listdir(datacard_path) if os.path.isdir(os.path.join(datacard_path, folder))]
if not signal_folders:
    print "Found no signal directory inside %s"%datacard_path
for signal_folder in signal_folders:
    sig_path = os.path.join(datacard_path, signal_folder)
    postfit_file = os.path.join(sig_path, postfit_tmp.replace('SIG', signal_folder))

    if os.path.isfile(postfit_file): f = TFile.Open(postfit_file)
    else:
        print "Found no postfit root file in directory %s"%os.path.join(datacard_path, signal_folder)
        continue

    tmp_str = ''

    for htmp in hnames:
        for proc in procs + [signal_folder]:

            ratio = 1.
            if f.Get(os.path.join(htmp.replace('SIG',signal_folder)+'_postfit', proc)):
              hname = htmp.replace('SIG',signal_folder)
              h_prefit  = f.Get(os.path.join(hname+'_prefit', proc))
              h_postfit = f.Get(os.path.join(hname+'_postfit', proc))

              if h_prefit.Integral > 0.: ratio = h_postfit.Integral() / h_prefit.Integral()
              tmp_str += signal_folder + ',' + hname + ',' + proc + ',' + str(round(ratio, 4)) + '\n'

    fout = open(postfit_file.replace('SIG', signal_folder).replace('.root', '_scale.txt'), 'w')
    print>>fout, tmp_str
    print "Write postfit scales in " + postfit_file.replace('SIG', signal_folder).replace('.root', '_scale.txt')


