import ROOT
import os, sys
ROOT.gROOT.SetBatch(ROOT.kTRUE)
rootfilename = sys.argv[1]
rootfile = ROOT.TFile(rootfilename)
canvas = ROOT.TCanvas()
rootfile.GetObject('nuisances', canvas)
canvas.SetBottomMargin(0.3)
canvas.SetRightMargin(0.03)
canvas.SetLeftMargin(0.07)

print rootfilename
canvas.Print(rootfilename.replace(".root", ".png"))

