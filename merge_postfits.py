import os, sys
import ROOT
from ROOT import *

print "Usage: python merge_postfit.py fullRun2Comb_folder"

path = 'postfit_shapes_TOP_LFV_forPlotIt'
files = os.listdir(path)

for fname in files:
    if not fname.endswith('.root') or 'plots.root' in fname: continue
    f_org = TFile.Open(os.path.join(path, fname))

    # as there is only one channal per coupling, seems like the combine tool removes 'DNN' string (process)
    prefix = 'DNN'
    histos = ['']
    year_list = list(set([i.GetName()[5:] for i in f_org.GetListOfKeys() if '__' not in i.GetName()]))
    #year_list = ['2016pre', '2016post', '2017', '2018'] #control postfit
    if not any(i in fname for i in ['data', 'totalup', 'totaldown']): vars = ['', '__postfitup', '__postfitdown']
    else: vars = ['']
 
    hist_list = []

    for hbase in histos:
        for var in vars:
            h_ = f_org.Get('year_' + year_list[0] + hbase + var)
            #h_ = f_org.Get('ch2_year_' + year_list[0] + hbase + var) #control postfit
            h_.SetDirectory(0)
            year_num = 1
            while year_num < len(year_list):
                h_tmp = f_org.Get('year_' + year_list[year_num] + hbase + var).Clone(hbase + var)
                #h_tmp = f_org.Get('ch2_year_' + year_list[year_num] + hbase + var).Clone(hbase + var) #control postfit
                h_tmp.SetDirectory(0)
                h_.Add(h_tmp, 1.0)
                year_num += 1

            h_.SetName(prefix + hbase + var)
            hist_list.append(h_)

    f_new = TFile.Open(os.path.join(path, fname), 'RECREATE')
    for h in hist_list: h.Write()
    f_new.Write()
    f_new.Close()
