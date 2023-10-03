import os, sys
import numpy as np
import statsmodels.api as sm
import ROOT
from ROOT import *

base_path = sys.argv[1]
f_in = sys.argv[2]
year = sys.argv[3]

print "Start smoothening on shapes..."

def smoothing(hin, hnom):

  htmp = hin.Clone()
  htmp.SetDirectory(0)
  htmp.Divide(hnom)

  x_vals = np.arange(htmp.GetNbinsX())
  y_vals = np.zeros(htmp.GetNbinsX())

  for i in xrange(htmp.GetNbinsX()):
    y_vals[i] = htmp.GetBinContent(i+1)

  #local linear regression (locally weighted polynomial regression)
  lowess = sm.nonparametric.lowess
  smoothed_vals = np.zeros(y_vals.shape)
  smoothed_vals = lowess(y_vals, x_vals, frac=2./3, return_sorted=False)

  for x_position in x_vals:
    hin.SetBinContent(x_position+1, max(0, smoothed_vals[x_position]*hnom.GetBinContent(x_position+1)))

  return hin



if not os.path.isfile(f_in.rstrip('.root') + '_org.root'):
  os.rename( f_in, f_in.rstrip('.root') + '_org.root' )

f = TFile.Open( f_in.rstrip('.root') + '_org.root', "READ")
f_new = TFile.Open( f_in, "RECREATE")


dir_ = "DNN"
print(dir_, year)
f_dir = f.Get(dir_)
f_new.mkdir(dir_)
f_new.cd(dir_)

histo_list = []
histo_list = [x.GetName() for x in f_dir.GetListOfKeys()]

for histos in histo_list:
  h = f_dir.Get(histos)
  h.SetDirectory(ROOT.nullptr)
  hname = h.GetName()

  if ('tune' in hname):
     h_nom = f_dir.Get(hname[:hname.rfind('__')])
     h_nom.SetDirectory(ROOT.nullptr)
     h = smoothing(h, h_nom)

  h.Write()

f_new.Write()
f_new.Close()
f.Close()
