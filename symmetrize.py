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
  smoothed_vals = lowess(y_vals, x_vals, frac=2.5/3, return_sorted=False)

  #for i in xrange(htmp.GetNbinsX()):
  #  if i == 0: y_vals[i] = htmp.GetBinContent(i+1)
  #  elif i > 0 and i < htmp.GetNbinsX() -1: y_vals[i] = (htmp.GetBinContent(i) + htmp.GetBinContent(i+1) + htmp.GetBinContent(i+2))/3
  #  elif i == htmp.GetNbinsX() - 1: y_vals[i] = (htmp.GetBinContent(i) + htmp.GetBinContent(i+1))/2


  for x_position in x_vals:
    hin.SetBinContent(x_position+1, max(0, smoothed_vals[x_position]*hnom.GetBinContent(x_position+1)))
    #hin.SetBinContent(x_position+1, max(0, y_vals[x_position]*hnom.GetBinContent(x_position+1)))

  return hin


def symmetrize(var, var_opp, nom):

    for xbin in xrange(var.GetNbinsX()):
      if nom.GetBinContent(xbin+1) == 0: ratio = 1.
      else:
        ratio = var.GetBinContent(xbin+1) / nom.GetBinContent(xbin+1)
        ratio_opp = 1.
        if var_opp.GetBinContent(xbin+1) > 0: ratio_opp = var.GetBinContent(xbin+1) / var_opp.GetBinContent(xbin+1)

        diff = abs(nom.GetBinContent(xbin+1)-var.GetBinContent(xbin+1)) + abs(nom.GetBinContent(xbin+1)-var_opp.GetBinContent(xbin+1))
        if ratio_opp > 1.:
          var.SetBinContent(xbin+1, nom.GetBinContent(xbin+1) + diff/2.)
          if ratio > 1.2: var.SetBinContent(xbin+1, 1.2 * nom.GetBinContent(xbin+1))
        else:
          var.SetBinContent(xbin+1, nom.GetBinContent(xbin+1) - diff/2.)
          if ratio < 0.8: var.SetBinContent(xbin+1, 0.8 * nom.GetBinContent(xbin+1))
          if nom.GetBinContent(xbin+1) - diff/2. < 0.: var.SetBinContent(xbin+1, 0)

    return var


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

  if ('tune' in hname) or ('hdamp' in hname) or ('jes' in hname and 'other' in hname) or ('jer' in hname and 'other' in hname):
    h_nom = f_dir.Get(hname[:hname.rfind('__')])
    h_nom.SetDirectory(ROOT.nullptr)
    h = smoothing(h, h_nom)

    #if 'Down' in hname:
    #  h_opp = f_dir.Get(hname.replace('Down','Up'))
    #  h_opp = smoothing(h_opp, h_nom)
    #elif 'Up' in hname:
    #  h_opp = f_dir.Get(hname.replace('Up','Down'))
    #  h_opp = smoothing(h_opp, h_nom)
    #  h_opp.SetDirectory(ROOT.nullptr)
    #  h = symmetrize(h, h_opp, h_nom)
     
  h.Write()

f_new.Write()
f_new.Close()
f.Close()
