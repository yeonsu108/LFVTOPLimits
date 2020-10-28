import os, sys
import ROOT
from ROOT import *

print "Usage: python merge_postfit.py datacard_folder years"

signal = sys.argv[1]
years = sys.argv[2]

path = 'postfit_shapes_FCNC_'+signal+'_Discriminant_DNN_'+signal+'_'+years+'_all_forPlotIt'
files = os.listdir(path)

for fname in files:
    if not fname.endswith('.root') or 'plots.root' in fname: continue
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
                h_tmp.SetDirectory(0)
                h_.Add(h_tmp, 1.0)
                year_num += 1

            h_.SetName(hbase + var)
            hist_list.append(h_)

    f_new = TFile.Open(os.path.join(path, fname), 'RECREATE')
    for h in hist_list: h.Write()
    f_new.Write()
    f_new.Close()
