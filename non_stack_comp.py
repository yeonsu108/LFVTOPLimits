import os
from collections import OrderedDict
import ROOT
from ROOT import *

gROOT.SetBatch(kTRUE)

#input_path = 'datacards_201215_2017v6_ttbbUnc_smoothTuneHdamp/'
input_path = 'datacards_201215_2018v6_ttbbUnc_smoothTuneHdamp/'

couplings = ['Hct', 'Hut']
jet_bins = ['b2j3', 'b3j3', 'b2j4', 'b3j4', 'b4j4']
rootfile_template = 'shapes_DNN_COUPLING_all.root'
process_list_org = ['ttbb', 'ttcc', 'ttlf', 'other', 'qcd']
color_code_org = [636, 634, 633, 801, 17]

plot_dir = 'compare_shapes_' + input_path
if not os.path.isdir(plot_dir):
    os.mkdir(plot_dir)

l = TLegend(0.12,0.83,0.75,0.88)
l.SetNColumns(6);
l.SetTextSize(0.04);
l.SetLineColor(0);
l.SetFillColor(0);

for coupling in couplings:
    process_list = process_list_org[:]
    process_list.append(coupling)
    for jet_bin in jet_bins:
        rootfile_name = rootfile_template.replace('COUPLING', coupling)
        rootfile_path = os.path.join(input_path, rootfile_name)
        rootfile = TFile(rootfile_path)
        dir_in_rootfile = "DNN_" + coupling + "_" + jet_bin
        rootdir = rootfile.GetDirectory(dir_in_rootfile)
        #hist_list = [x.GetName() for x in rootdir.GetListOfKeys() if not any(i in x.GetName() for i in ['Up','Down'])]

        plot_name = coupling + '_' + jet_bin
        canvas = TCanvas(plot_name, plot_name, 500, 500)

        hist_list_org = OrderedDict()
        hist_list_org[rootfile.Get(dir_in_rootfile + "/ttbb")] = 636
        hist_list_org[rootfile.Get(dir_in_rootfile + "/ttcc")] = 634
        hist_list_org[rootfile.Get(dir_in_rootfile + "/ttlf")] = 633
        hist_list_org[rootfile.Get(dir_in_rootfile + "/other")] = 801
        hist_list_org[rootfile.Get(dir_in_rootfile + "/qcd")] = 15 #originally 17

        if coupling == 'Hut': hist_list_org[rootfile.Get(dir_in_rootfile + "/Hut")] = 403
        else :                hist_list_org[rootfile.Get(dir_in_rootfile + "/Hct")] = 601

        max_list = []
        hist_list = OrderedDict()
        for h, col in hist_list_org.items():
            if h.Integral() > 0:
                h.Scale(1/h.Integral())
            hist_list[h] = col
            max_list.append(h.GetMaximum())

        for h, col in hist_list.items():
            h.GetYaxis().SetRangeUser(0,max(max_list)*1.2)
            h.SetLineColor(col)
            h.SetLineWidth(2)
            h.SetStats(0)
            h.SetTitle("Normalized BDT Score")
            if 'qcd' in h.GetName(): h.Draw('hist same e')
            else: h.Draw('hist same')
            l.AddEntry(h, h.GetName(), 'f')

        l.Draw('same')

        label = TPaveText(0.76, 0.83, 0.89, 0.88, 'blNDC')
        label.SetShadowColor(0)
        label.SetFillColor(0)
        label.SetTextSize(0.04)
        label.SetTextFont(42)
        label.AddText(coupling + ', ' + jet_bin)
        label.Draw('same')

        canvas.Print(os.path.join(plot_dir, plot_name + '.pdf'))
        canvas.Clear()
        l.Clear()
