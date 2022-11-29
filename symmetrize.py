import os, sys
import numpy as np
#import statsmodels.api as sm
from ROOT import *
import ROOT

base_path = sys.argv[1]
f_in = sys.argv[2]
year = sys.argv[3]

print "Start symmetrization on shapes..."


def fwhm2sigma(fwhm):

  return fwhm / np.sqrt(8 * np.log(2))


def smoothing(hin, hnom, fwhm):

  htmp = hin.Clone()
  htmp.SetDirectory(0)
  #htmp.Add(hnom, -1.0)
  htmp.Divide(hnom)

  x_vals = np.arange(htmp.GetNbinsX())
  y_vals = np.zeros(htmp.GetNbinsX())

  for i in xrange(htmp.GetNbinsX()):
    y_vals[i] = htmp.GetBinContent(i+1)

  #Kernel smoothing
  #FWHM = fwhm
  #sigma = fwhm2sigma(FWHM)

  #for x_position in x_vals:
  #  kernel = np.exp(-(x_vals - x_position) ** 2 / (2 * sigma ** 2))
  #  kernel = kernel / sum(kernel)
  #  #hin.SetBinContent(x_position+1, max(0, sum(y_vals * kernel)))
  #  hin.SetBinContent(x_position+1, max(0, sum(y_vals * kernel)+hnom.GetBinContent(x_position+1)))
  #  #hin.SetBinContent(x_position+1, max(0, sum(y_vals * kernel)*hnom.GetBinContent(x_position+1)))

  #local linear regression (locally weighted polynomial regression)
  #lowess = sm.nonparametric.lowess
  smoothed_vals = np.zeros(y_vals.shape)
  #smoothed_vals = lowess(y_vals, x_vals, frac=2./3, return_sorted=False)

  for x_position in x_vals:
    #hin.SetBinContent(x_position+1, max(0, smoothed_vals[x_position]))
    #hin.SetBinContent(x_position+1, max(0, smoothed_vals[x_position]+hnom.GetBinContent(x_position+1)))
    hin.SetBinContent(x_position+1, max(0, smoothed_vals[x_position]*hnom.GetBinContent(x_position+1)))

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

dir_list = []
dir_list = [x.GetName() for x in f.GetListOfKeys()]

for dir_ in dir_list:
  print("In symmetrize :",dir_, year)
  f_dir = f.Get(dir_)
  f_new.mkdir(dir_)
  f_new.cd(dir_)

  histo_list = []
  histo_list = [x.GetName() for x in f_dir.GetListOfKeys()]

  for histos in histo_list:
    h = f_dir.Get(histos)
    h.SetDirectory(ROOT.nullptr)
    hname = h.GetName()

    #Special treatements
    if year == '2017':
      if ( ('jec' in hname and any(name in hname for name in ['qcd']) and 'b2j3' in dir_)
        or ('jer' in hname and any(name in hname for name in ['qcd']) and 'b2j3' in dir_)
        or ('pdf' in hname and any(name in hname for name in ['ttbb']) and 'b3j3' in dir_)
        #or ('Tune' in hname and any(sname in dir_ for sname in ['b2j3', 'b2j4']))
        #or ('hdamp' in hname and any(sname in dir_ for sname in ['b2j3', 'b3j4','b3j3'])) ):
        or (any(s in hname for s in ['Tune', 'hdamp',])) ):

        if 'Down' in hname:
          h_opp = f_dir.Get(hname.replace('Down','Up'))
        elif 'Up' in hname:
          h_opp = f_dir.Get(hname.replace('Up','Down'))
        h_opp.SetDirectory(ROOT.nullptr)

        h_nom = f_dir.Get(hname[:hname.rfind('__')])
        h_nom.SetDirectory(ROOT.nullptr)

        if any(s in hname for s in ['Tune', 'hdamp',]):
          smoothing(h, h_nom, 2)
          smoothing(h_opp, h_nom, 2)
          symmetrize(h, h_opp, h_nom)

        else:
          h_nom = f_dir.Get(hname[:hname.rfind('__')])
          h_nom.SetDirectory(ROOT.nullptr)
          symmetrize(h, h_opp, h_nom)


    elif year == '2018':
      if ( ('jec' in hname and any(name in hname for name in ['qcd']) and 'b2j3' in dir_)
        or ('pdf' in hname and any(name in hname for name in ['ttbb','ttcc','ttlf']) and 'b4j4' in dir_)
        or ('cferr1' in hname and any(name in hname for name in ['other']) and 'b4j4' in dir_)
        or (any(s in hname for s in ['Tune', 'hdamp',])) ):

        if 'Down' in hname:
          h_opp = f_dir.Get(hname.replace('Down','Up'))
        elif 'Up' in hname:
          h_opp = f_dir.Get(hname.replace('Up','Down'))
        h_opp.SetDirectory(ROOT.nullptr)

        h_nom = f_dir.Get(hname[:hname.rfind('__')])
        h_nom.SetDirectory(ROOT.nullptr)

        if any(s in hname for s in ['Tune', 'hdamp',]):
          smoothing(h, h_nom, 2)
          smoothing(h_opp, h_nom, 2)
          symmetrize(h, h_opp, h_nom)

        else:
          h_nom = f_dir.Get(hname[:hname.rfind('__')])
          h_nom.SetDirectory(ROOT.nullptr)
          symmetrize(h, h_opp, h_nom)

    h.Write()

f_new.Write()
f_new.Close()
f.Close()
