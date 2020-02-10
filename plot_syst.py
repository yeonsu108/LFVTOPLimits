import os
import ROOT

ROOT.gROOT.SetBatch(ROOT.kTRUE)

input_path = 'datacards_200101_2017/'
year = '2017'

couplings = ['Hct', 'Hut']
jet_bins = ['b2j3', 'b3j3', 'b2j4', 'b3j4', 'b4j4']
rootfile_template = 'FCNC_COUPLING_Discriminant_DNN_COUPLING_JETBIN_shapes.root'
process_list_org = ['ttlf', 'ttcc', 'ttbb', 'other']

plot_dir = 'systematics_plots_' + input_path
if not os.path.isdir(plot_dir):
    os.mkdir(plot_dir)

for coupling in couplings:
    process_list = process_list_org[:]
    process_list.append(coupling)
    for jet_bin in jet_bins:
        rootfile_name = rootfile_template.replace("COUPLING", coupling).replace("JETBIN", jet_bin)
        rootfile_path = os.path.join(input_path, coupling, rootfile_name)
        print rootfile_path
        rootfile = ROOT.TFile(rootfile_path)
        dir_in_rootfile = "DNN_" + coupling + "_" + jet_bin
        rootdir = rootfile.GetDirectory(dir_in_rootfile)
        hist_list_org = [x.GetName() for x in rootdir.GetListOfKeys()]
        syst_list = []
        for it in hist_list_org:
            if 'Up' in it: syst_list.append(it[it.find('_')+1:-2])
        for syst in syst_list:
            print syst
            syst_name = syst + "_" + coupling + "_" + jet_bin
            for proc in process_list:
                plot_name = syst_name + "_" + proc 
                canvas = ROOT.TCanvas(plot_name, plot_name)
                nominal_th1 = rootfile.Get(dir_in_rootfile + "/" + proc)
                shape_up = rootfile.Get(dir_in_rootfile + "/" + proc + "_" + syst + "Up")
                if not shape_up:
                    print "No TH1 for " + syst + " " + proc
                    continue
                shape_down = rootfile.Get(dir_in_rootfile + "/" + proc + "_" + syst + "Down")
                ratio_up = nominal_th1.Clone()
                ratio_up.Divide(shape_up)
                ratio_up.SetLineColor(ROOT.kRed)
                ratio_down = nominal_th1.Clone()
                ratio_down.Divide(shape_down)
                legend = ROOT.TLegend(0.25, 0.75, 0.55, 0.9, syst)
                legend.AddEntry(ratio_up, "Nom/Up")
                legend.AddEntry(ratio_down, "Nom/Down")
                line = ROOT.TLine(-1, 1, 1, 1)
                line.SetLineStyle(2)
                minmax = [ratio_up.GetMaximum(), ratio_up.GetMinimum(), ratio_down.GetMaximum(), ratio_down.GetMinimum()]
                ratio_up.GetYaxis().SetRangeUser(min(minmax)*0.9, max(minmax)*1.1)
                ratio_up.Draw()
                ratio_down.Draw('same')
                legend.Draw()
                line.Draw()
                canvas.Print(os.path.join(plot_dir, plot_name + '.png'))



        









