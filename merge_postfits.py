import os, sys
import ROOT
from ROOT import *

print "Usage: python merge_postfit.py datacard_folder years"

current_dir = os.getcwd()
datacard_path = sys.argv[1]
years = sys.argv[2]

signal_folders = [folder for folder in os.listdir(datacard_path) if os.path.isdir(os.path.join(datacard_path, folder))]
if not signal_folders:
    print "Found no signal directory inside %s"%datacard_path
for signal_folder in signal_folders:
    if signal_folder == 'Hct': continue
    path = os.path.join(datacard_path, os.path.join(signal_folder,'postfit_shapes_FCNC_Hut_Discriminant_DNN_'+signal_folder+'_'+years+'_all_forPlotIt'))
    files = os.listdir(path)

    for fname in files:
        f_org = TFile.Open(os.path.join(path, fname))

        histos = list(dict.fromkeys([i.GetName()[10:] for i in f_org.GetListOfKeys()]))
        histos = [x for x in histos if not '__' in x]
        year_list = [years[i:i+2] for i in range(0, len(years), 2)]
        if 'data' not in fname: vars = ['', '__postfitup', '__postfitdown']
        else: vars = ['']
        
        hist_list = []

        for hbase in histos:
            for var in vars:
                h_ = f_org.Get('year_20' + year_list[0] + '_' + hbase + var)
                h_.SetDirectory(0)
                year_num = 1
                while year_num < len(year_list):
                    h_tmp = f_org.Get('year_20' + year_list[year_num] + '_' + hbase + var).Clone(hbase + var)
                    h_.Add(h_tmp, 1.0)
                    year_num += 1

                h_.SetName(hbase + var)
                hist_list.append(h_tmp)

        f_new = TFile.Open(os.path.join(path, fname), 'RECREATE')
        for h in hist_list: h.Write()
        f_new.Write()
        f_new.Close()
