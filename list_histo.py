from ROOT import *

file_name = '/afs/cern.ch/work/b/brfranco/public/kTupleMaker/rootfiles/th1_with_syst_for_plotit/legacy/STFCNC01/hist_TTpowhegttcc.root'
rootfile = TFile(file_name)

histolist = rootfile.GetListOfKeys()
for key in histolist:
  #if 'h_LepPt' in key.GetName() and '__scale0' in key.GetName():
  #if 'h_LepPt_Ch1_S4' in key.GetName():
  #if '_Ch1_S4' in key.GetName() and '__' not in key.GetName():
  if 'h_LepPt' in key.GetName() and '_Ch1_S4' in key.GetName():
    print key.GetName()
