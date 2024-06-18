import json, sys, os, argparse
from math import sqrt
from array import array
from ROOT import *
import numpy as np
import math
gROOT.SetBatch()
gROOT.ProcessLine(".x setTDRStyle.C")

parser = argparse.ArgumentParser(description='Store limits inside a json file and plot them if required (one bin per category).')
parser.add_argument('--limitfolder', dest='limitfolder', default='./datacards', type=str, help='Folder where ct and ut combine output folders are stored')
parser.add_argument('--unblind', dest='unblind', action='store_true', default=True, help='Display or not the observed limit.')
parser.add_argument('--lumi', dest='lumi', type=str, default='138', help='Luminosity to display on the plot.')
parser.add_argument('--pas', dest='pas', type=bool, default=True, help='To present Preliminary label')

options = parser.parse_args()
print options.limitfolder

postfix = ''

signal_Xsec = {'st_lfv_cs': 6.4, 'st_lfv_cv': 41.0, 'st_lfv_ct': 225.2, 'st_lfv_us': 61.83, 'st_lfv_uv': 297.6, 'st_lfv_ut': 1401}
signal_lorentz_dict = {'s': kRed+1, 'v': kGreen+2, 't': kBlue+1}
#signal_lorentz_dict = {'t': kBlue+1}

def calcWilson(limits):
    wilson = np.sqrt(limits)
    return wilson

def calcBr(op, limits):
    if op == "cs" or op == "us":
        out = 2 * limits * (172.5**5) * 10**(-6) / (1.32 * 6144 * (math.pi**3))
    elif op == "cv" or op == "uv":
        out = 4 * limits * (172.5**5) * 10**(-6) / (1.32 * 1536 * (math.pi**3))
    elif op == "ct" or op == "ut":
        out = 2 * limits * (172.5**5) * 10**(-6) / (1.32 * 128*(math.pi**3))
    return out

x_coup_exp = {}; y_coup_exp = {}
x_coup_obs = {}; y_coup_obs = {}
x_coup_one_up = {}; x_coup_one_dn = {}
y_coup_one_up = {}; y_coup_one_dn = {}
x_br_exp = {}; y_br_exp = {}
x_br_obs = {}; y_br_obs = {}
x_br_one_up = {}; x_br_one_dn = {}
y_br_one_up = {}; y_br_one_dn = {}

ut_exp = {}; ut_obs = {}; ut_one_up = {}; ut_one_dn = {}
ct_exp = {}; ct_obs = {}; ct_one_up = {}; ct_one_dn = {}

for signal_lorentz in signal_lorentz_dict:
    ut_limits = json.loads(open(os.path.join(options.limitfolder, 'st_lfv_u' + signal_lorentz + '_limits.json')).read())
    ct_limits = json.loads(open(os.path.join(options.limitfolder, 'st_lfv_c' + signal_lorentz + '_limits.json')).read())

    x_coup_exp[signal_lorentz], y_coup_exp[signal_lorentz] = array( 'd' ), array( 'd' )
    x_coup_obs[signal_lorentz], y_coup_obs[signal_lorentz] = array( 'd' ), array( 'd' )
    x_coup_one_up[signal_lorentz], x_coup_one_dn[signal_lorentz] = array( 'd' ), array( 'd' )
    y_coup_one_up[signal_lorentz], y_coup_one_dn[signal_lorentz] = array( 'd' ), array( 'd' )
    x_br_exp[signal_lorentz], y_br_exp[signal_lorentz] = array( 'd' ), array( 'd' )
    x_br_obs[signal_lorentz], y_br_obs[signal_lorentz] = array( 'd' ), array( 'd' )
    x_br_one_up[signal_lorentz], x_br_one_dn[signal_lorentz] = array( 'd' ), array( 'd' )
    y_br_one_up[signal_lorentz], y_br_one_dn[signal_lorentz] = array( 'd' ), array( 'd' )

    ut_exp[signal_lorentz] = ut_limits[""]['expected']
    ut_obs[signal_lorentz] = ut_limits[""]['observed']
    ut_one_up[signal_lorentz] = ut_limits[""]['one_sigma'][1]
    ut_one_dn[signal_lorentz] = ut_limits[""]['one_sigma'][0]

    ct_exp[signal_lorentz] = ct_limits[""]['expected']
    ct_obs[signal_lorentz] = ct_limits[""]['observed']
    ct_one_up[signal_lorentz] = ct_limits[""]['one_sigma'][1]
    ct_one_dn[signal_lorentz] = ct_limits[""]['one_sigma'][0]

def coupl(ut_limit, ct_limit, pos, arrX, arrY, to_print):
    if pow(pos, 2) <= ut_limit:
        coupling = sqrt(ct_limit * (1 - pow(pos, 2)/ut_limit))
        arrX.append(pos)
        arrY.append(coupling)
        if to_print: print pos, ' : coupling -> ', coupling

def br(op, ut_limit, ct_limit, pos, arrX, arrY, to_print):
    if pow(pos, 2) <= ut_limit:
        coupling = sqrt(ct_limit * (1 - pow(pos, 2)/ut_limit))
        br_x = calcBr(op, pow(pos, 2))
        br_y = calcBr(op, pow(coupling, 2))
        #arrX.append(np.around(br_x, decimals=5))
        #arrY.append(np.around(br_y, decimals=5))
        arrX.append(br_x)
        arrY.append(br_y)
        #if to_print: print pos, ' : br -> ', 10**-6 * br_x, 10**-6 * br_y
        if to_print: print pos, op, ' : br -> ', br_x, br_y


for i in xrange(200000):
    x_pos = 0.000005 * i

    to_print = False
    if (x_pos * 400).is_integer(): to_print = True

    for signal_lorentz in signal_lorentz_dict:
        coupl(ut_exp[signal_lorentz], ct_exp[signal_lorentz], x_pos, x_coup_exp[signal_lorentz], y_coup_exp[signal_lorentz], to_print)
        coupl(ut_obs[signal_lorentz], ct_obs[signal_lorentz], x_pos, x_coup_obs[signal_lorentz], y_coup_obs[signal_lorentz], to_print)
        coupl(ut_one_up[signal_lorentz], ct_one_up[signal_lorentz], x_pos, x_coup_one_up[signal_lorentz], y_coup_one_up[signal_lorentz], to_print)
        coupl(ut_one_dn[signal_lorentz], ct_one_dn[signal_lorentz], x_pos, x_coup_one_dn[signal_lorentz], y_coup_one_dn[signal_lorentz], to_print)

        br('u'+signal_lorentz, ut_exp[signal_lorentz], ct_exp[signal_lorentz], x_pos, x_br_exp[signal_lorentz], y_br_exp[signal_lorentz], to_print)
        br('u'+signal_lorentz, ut_obs[signal_lorentz], ct_obs[signal_lorentz], x_pos, x_br_obs[signal_lorentz], y_br_obs[signal_lorentz], to_print)
        br('u'+signal_lorentz, ut_one_up[signal_lorentz], ct_one_up[signal_lorentz], x_pos, x_br_one_up[signal_lorentz], y_br_one_up[signal_lorentz], to_print)
        br('u'+signal_lorentz, ut_one_dn[signal_lorentz], ct_one_dn[signal_lorentz], x_pos, x_br_one_dn[signal_lorentz], y_br_one_dn[signal_lorentz], to_print)


##########################################
#           Wilson coefficient           #
##########################################
g_coup_exp = {}; g_coup_obs = {}
g_coup_one_band = {};

# Create Canvas
c1 = TCanvas("c1","interpolate",450,400)
c1.SetLeftMargin(0.15)
p1 = c1.DrawFrame(0, 0.002, 0.3, 1.4)

# Create TGraph
for signal_lorentz in signal_lorentz_dict:
    g_coup_exp[signal_lorentz] = TGraph(len(x_coup_exp[signal_lorentz]), x_coup_exp[signal_lorentz], y_coup_exp[signal_lorentz])
    g_coup_obs[signal_lorentz] = TGraph(len(x_coup_obs[signal_lorentz]), x_coup_obs[signal_lorentz], y_coup_obs[signal_lorentz])
    print 'ut obs Wilson ',  x_coup_obs[signal_lorentz][-1], 'ct obs kappa', y_coup_obs[signal_lorentz][0]
    print 'ut exp Wilson ',  x_coup_exp[signal_lorentz][-1], 'ct exp kappa', y_coup_exp[signal_lorentz][0]
    print 'ut exp +1sig Wilson ',  x_coup_one_up[signal_lorentz][-1], 'ct exp kappa', y_coup_one_up[signal_lorentz][0]
    print 'ut exp -1sig Wilson ',  x_coup_one_dn[signal_lorentz][-1], 'ct exp kappa', y_coup_one_dn[signal_lorentz][0]

    g_coup_one_band[signal_lorentz] = TGraph(len(x_coup_one_up[signal_lorentz])+len(x_coup_one_dn[signal_lorentz]))
    for i in xrange(len(x_coup_one_up[signal_lorentz])):
        g_coup_one_band[signal_lorentz].SetPoint(i, x_coup_one_up[signal_lorentz][i], y_coup_one_up[signal_lorentz][i]);
        if len(x_coup_one_up[signal_lorentz]) + i < len(x_coup_one_up[signal_lorentz])+len(x_coup_one_dn[signal_lorentz]):
            g_coup_one_band[signal_lorentz].SetPoint(len(x_coup_one_up[signal_lorentz]) + i , x_coup_one_dn[signal_lorentz][len(x_coup_one_dn[signal_lorentz])-i-1], y_coup_one_dn[signal_lorentz][len(x_coup_one_dn[signal_lorentz])-i-1]);


    # Change style
    g_coup_exp[signal_lorentz].SetLineColor(signal_lorentz_dict[signal_lorentz])
    g_coup_exp[signal_lorentz].SetLineWidth(3)
    g_coup_exp[signal_lorentz].SetLineStyle(2)
    g_coup_obs[signal_lorentz].SetLineColor(signal_lorentz_dict[signal_lorentz])
    g_coup_obs[signal_lorentz].SetLineWidth(3)
    if not options.unblind:
        g_coup_obs[signal_lorentz].SetLineColorAlpha(kRed, 0.0);
    g_coup_one_band[signal_lorentz].SetFillColorAlpha(signal_lorentz_dict[signal_lorentz], 0.3)
    g_coup_one_band[signal_lorentz].SetLineWidth(0)


# Axis style
xAxis = p1.GetXaxis()
xAxis.SetTitle("C_{tu#mu#tau}/#Lambda^{2} (TeV^{-2})")
xAxis.SetLabelSize(0.05)
xAxis.SetLabelFont(42)
xAxis.SetTitleFont(42)
xAxis.SetTitleOffset(1.0)
xAxis.SetTitleSize(0.053)
yAxis = p1.GetYaxis()
yAxis.SetTitle("C_{tc#mu#tau}/#Lambda^{2} (TeV^{-2})")
yAxis.SetLabelSize(0.05)
yAxis.SetLabelFont(42)
yAxis.SetTitleFont(42)
yAxis.SetTitleOffset(1.3)
yAxis.SetTitleSize(0.053)


# Some text
progress = 'Preliminary'
latexLabel = TLatex()
latexLabel.SetTextSize(0.8 * c1.GetTopMargin())
latexLabel.SetNDC()
#Lumi
latexLabel.SetTextFont(62) # helvetica
latexLabel.DrawLatex(0.71, 0.96, '%s fb^{-1} (13 TeV)'%(options.lumi))
#CMS
latexLabel.SetTextFont(62) # helvetica bold face
latexLabel.SetTextSize(1.00 * c1.GetTopMargin())
latexLabel.DrawLatex(0.19, 0.87, "CMS")
#legend
latexLabel.SetTextFont(62)
latexLabel.SetTextSize(0.65 * c1.GetTopMargin())
latexLabel.DrawLatex(0.63, 0.88, "CLFV     Exp #pm 1#sigma   Obs")
latexLabel.DrawLatex(0.63, 0.84, "Scalar")
latexLabel.DrawLatex(0.63, 0.80, "Vector")
latexLabel.DrawLatex(0.63, 0.76, "Tensor")
latexLabel.DrawLatex(0.63, 0.715, "95% CL upper limits")

if options.pas:
    latexLabel.SetTextFont(52) # helvetica italics
    latexLabel.SetTextSize(0.7 * c1.GetTopMargin())
    latexLabel.DrawLatex(0.19, 0.82, progress)

latexLabel.Clear()


# Legend
legend = TLegend(0.74, 0.75, 0.92, 0.87)
legend.SetNColumns(2)
legend.SetColumnSeparation(0.0)
legend.SetMargin(1.0)
legend.SetTextFont(42)
legend.SetTextColor(kWhite)
legend.SetFillStyle(0)
legend.SetLineColor(kWhite)

for signal_lorentz in signal_lorentz_dict:

    g_coup_one_band[signal_lorentz].Draw("f same")
    g_coup_obs[signal_lorentz].Draw("c same")
    g_coup_exp[signal_lorentz].Draw("c same")

    g_coup_one_band[signal_lorentz].SetLineColorAlpha(signal_lorentz_dict[signal_lorentz], 1.0)
    g_coup_one_band[signal_lorentz].SetLineStyle(2)
    g_coup_one_band[signal_lorentz].SetLineWidth(2)
    legend.AddEntry(g_coup_one_band[signal_lorentz], '............', 'lf')
    legend.AddEntry(g_coup_obs[signal_lorentz], '.', 'l')

gPad.RedrawAxis();
legend.Draw('same')
c1.cd()
if options.pas: c1.Print(options.limitfolder + "/interpolated_coupling"+postfix+"_pas.pdf")
else:           c1.Print(options.limitfolder + "/interpolated_coupling"+postfix+".pdf")

##########################################
#           branching fraction           #
##########################################
g_br_exp = {}; g_br_obs = {}
g_br_one_band = {};

c2 = TCanvas("c2","interpolate",450,400)
c2.SetLeftMargin(0.15)
p2 = c2.DrawFrame(0, 0.001, 0.27, 4.7)
#TGaxis.SetMaxDigits(2)
#TGaxis.SetExponentOffset(-0.03, -0.04, "x");
#TGaxis.SetExponentOffset(-0.07, 0.0, "y");

# Create TGraph
for signal_lorentz in signal_lorentz_dict:
    g_br_exp[signal_lorentz] = TGraph(len(x_br_exp[signal_lorentz]), x_br_exp[signal_lorentz], y_br_exp[signal_lorentz])
    g_br_obs[signal_lorentz] = TGraph(len(x_br_obs[signal_lorentz]), x_br_obs[signal_lorentz], y_br_obs[signal_lorentz])

    g_br_one_band[signal_lorentz] = TGraph(len(x_br_one_up[signal_lorentz])+len(x_br_one_dn[signal_lorentz]))
    for i in xrange(len(x_br_one_up[signal_lorentz])):
        g_br_one_band[signal_lorentz].SetPoint(i, x_br_one_up[signal_lorentz][i], y_br_one_up[signal_lorentz][i]);
        if len(x_br_one_up[signal_lorentz]) + i < len(x_br_one_up[signal_lorentz])+len(x_br_one_dn[signal_lorentz]):
            g_br_one_band[signal_lorentz].SetPoint(len(x_br_one_up[signal_lorentz]) + i , x_br_one_dn[signal_lorentz][len(x_br_one_dn[signal_lorentz])-i-1], y_br_one_dn[signal_lorentz][len(x_br_one_dn[signal_lorentz])-i-1]);


    # Change style
    g_br_exp[signal_lorentz].SetLineColor(signal_lorentz_dict[signal_lorentz])
    g_br_exp[signal_lorentz].SetLineWidth(3)
    g_br_exp[signal_lorentz].SetLineStyle(2)
    g_br_obs[signal_lorentz].SetLineColor(signal_lorentz_dict[signal_lorentz])
    g_br_obs[signal_lorentz].SetLineWidth(3)
    if not options.unblind:
        g_br_obs[signal_lorentz].SetLineColorAlpha(kRed, 0.0);
    g_br_one_band[signal_lorentz].SetFillColorAlpha(signal_lorentz_dict[signal_lorentz], 0.3)
    g_br_one_band[signal_lorentz].SetLineWidth(0)


# Axis style
xAxis = p2.GetXaxis()
#xAxis.SetTitle("BR_{ut}[%]")
xAxis.SetTitle("B(t#rightarrow #mu#tau u) #times 10^{-6}")
xAxis.SetLabelSize(0.05)
xAxis.SetLabelFont(42)
xAxis.SetTitleFont(42)
xAxis.SetTitleOffset(1.0)
xAxis.SetTitleSize(0.053)
yAxis = p2.GetYaxis()
#yAxis.SetTitle("BR_{ct}[%]")
yAxis.SetTitle("B(t#rightarrow #mu#tau c) #times 10^{-6}")
yAxis.SetLabelSize(0.05)
yAxis.SetLabelFont(42)
yAxis.SetTitleFont(42)
yAxis.SetTitleOffset(1.3)
yAxis.SetTitleSize(0.053)


# Some text
progress = 'Preliminary'
latexLabel = TLatex()
latexLabel.SetTextSize(0.8 * c1.GetTopMargin())
latexLabel.SetNDC()
#Lumi
latexLabel.SetTextFont(62) # helvetica
latexLabel.DrawLatex(0.71, 0.96, '%s fb^{-1} (13 TeV)'%(options.lumi))
#CMS
latexLabel.SetTextFont(62) # helvetica bold face
latexLabel.SetTextSize(1.00 * c1.GetTopMargin())
latexLabel.DrawLatex(0.19, 0.87, "CMS")
#legend
latexLabel.SetTextFont(62)
latexLabel.SetTextSize(0.65 * c1.GetTopMargin())
latexLabel.DrawLatex(0.63, 0.88, "CLFV     Exp #pm 1#sigma   Obs")
latexLabel.DrawLatex(0.63, 0.84, "Scalar")
latexLabel.DrawLatex(0.63, 0.80, "Vector")
latexLabel.DrawLatex(0.63, 0.76, "Tensor")
latexLabel.DrawLatex(0.63, 0.715, "95% CL upper limits")

if options.pas:
    latexLabel.SetTextFont(52) # helvetica italics
    latexLabel.SetTextSize(0.7 * c1.GetTopMargin())
    latexLabel.DrawLatex(0.19, 0.82, progress)

latexLabel.Clear()


# Legend
legend.Clear()
legend.SetNColumns(2)
legend.SetColumnSeparation(0.0)
legend.SetMargin(1.0)
legend.SetTextFont(42)
legend.SetTextColor(kWhite)
legend.SetFillStyle(0)
legend.SetLineColor(kWhite)

for signal_lorentz in signal_lorentz_dict:

    g_br_one_band[signal_lorentz].Draw("f same")
    g_br_obs[signal_lorentz].Draw("c same")
    g_br_exp[signal_lorentz].Draw("c same")

    g_br_one_band[signal_lorentz].SetLineColorAlpha(signal_lorentz_dict[signal_lorentz], 1.0)
    g_br_one_band[signal_lorentz].SetLineStyle(2)
    g_br_one_band[signal_lorentz].SetLineWidth(2)
    legend.AddEntry(g_br_one_band[signal_lorentz], '............', 'lf')
    legend.AddEntry(g_br_obs[signal_lorentz], '.', 'l')

gPad.RedrawAxis();
legend.Draw('same')

if options.pas: c2.Print(options.limitfolder + "/interpolated_br"+postfix+"_pas.pdf")
else:           c2.Print(options.limitfolder + "/interpolated_br"+postfix+".pdf")
