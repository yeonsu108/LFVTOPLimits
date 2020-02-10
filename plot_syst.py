import os
import ROOT

ROOT.gROOT.SetBatch(ROOT.kTRUE)

input_path = 'datacards_190702_2017/'
year = '2017'

couplings = ['Hct', 'Hut']
jet_bins = ['b2j3', 'b3j3', 'b2j4', 'b3j4', 'b4j4']
rootfile_template = 'FCNC_COUPLING_Discriminant_DNN_COUPLING_JETBIN_shapes.root'
process_list = ['Hct', 'ttlf', 'ttcc', 'ttbb', 'other']

#TOIMPROVE retrieve it by reading the rootfile content
syst_list = ['CMS_2017_cferr1','CMS_2017_cferr2','CMS_2017_elid','CMS_2017_elreco','CMS_2017_eltrg','CMS_2017_elzvtx','CMS_2017_hf','CMS_2017_hfstat1','CMS_2017_hfstat2','CMS_2017_jec','CMS_2017_jer','CMS_2017_lf','CMS_2017_lfstat1','CMS_2017_lfstat2','CMS_2017_muid','CMS_2017_muiso','CMS_2017_mutrg','CMS_2017_prefire','CMS_2017_pu','CMS_hdamp','CMS_pdf','CMS_ps','CMS_scale','Other_xsec','tt_xsec', 'CMS_TuneCP5']

plot_dir = 'systematics_plots_' + input_path
if not os.path.isdir(plot_dir):
    os.mkdir(plot_dir)

for coupling in couplings:
    for jet_bin in jet_bins:
        rootfile_name = rootfile_template.replace("COUPLING", coupling).replace("JETBIN", jet_bin)
        rootfile_path = os.path.join(input_path, coupling, rootfile_name)
        print rootfile_path
        rootfile = ROOT.TFile(rootfile_path)
        dir_in_rootfile = "DNN_" + coupling + "_" + jet_bin
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
                ratio_up.GetYaxis().SetRangeUser(0.5,1.5)
                ratio_down = nominal_th1.Clone()
                ratio_down.Divide(shape_down)
                legend = ROOT.TLegend(0.25, 0.75, 0.55, 0.9, syst)
                legend.AddEntry(ratio_up, "Nom/Up")
                legend.AddEntry(ratio_down, "Nom/Down")
                ratio_up.Draw()
                ratio_down.Draw('same')
                legend.Draw()
                canvas.Print(os.path.join(plot_dir, plot_name + '.png'))



        









