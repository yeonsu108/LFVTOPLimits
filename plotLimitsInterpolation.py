import json, sys, os, argparse
from math import sqrt
from array import array
from ROOT import *
gROOT.SetBatch()
gROOT.ProcessLine(".x setTDRStyle.C")

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1', 'True'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', 'False'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

parser = argparse.ArgumentParser(description='Store limits inside a json file and plot them if required (one bin per category).')
parser.add_argument('-limitfolder', dest='limitfolder', default='./datacards', type=str, help='Folder where Hct and Hut combine output folders are stored')
parser.add_argument('-category', dest='category', type=str, default='all', help='Bin name to draw. all, 1718_all, etc.')
parser.add_argument('-unblind', dest='unblind', type=str2bool, default="True", help='Display or not the observed limit.')
parser.add_argument('-lumi', dest='lumi', type=str, default='137', help='Luminosity to display on the plot.')
parser.add_argument('-pas', dest='pas', type=bool, default=False, help='To present Preliminary label')

options = parser.parse_args()

postfix = ''
Hctjson = 'Hct_limits.json'
Hutjson = 'Hut_limits.json'
if options.category != 'all':
  postfix = '_' + options.category
  Hctjson = 'Hct_limits_add.json'
  Hutjson = 'Hut_limits_add.json'

signal_Xsec_couplingOne = {"Hut": 1, "Hct": 1}  # for limit rescaling if the signal Xsec inseted in combine was not 1 pb
signal_Xsec_couplingOneForBR = {"Hut": 60.34, "Hct": 48.4} # to extract limit on BR: BR(t --> Hq) < XsecExcl*Width(t-->Hq)/(sigXsec * TotalWidth) = XsecExcl*0.19/(sigXsec * 1.32158) 

Hut_limits = json.loads(open(os.path.join(options.limitfolder, Hutjson)).read())
for key in Hut_limits:
  for number_type in Hut_limits[key]:
    if isinstance(Hut_limits[key][number_type], list):
      Hut_limits[key][number_type][0] = round(Hut_limits[key][number_type][0]*signal_Xsec_couplingOne['Hut'], 4)
      Hut_limits[key][number_type][1] = round(Hut_limits[key][number_type][1]*signal_Xsec_couplingOne['Hut'], 4)
    else:
      Hut_limits[key][number_type] = round(Hut_limits[key][number_type]*signal_Xsec_couplingOne['Hut'], 4)
#   if number_type == 'observed':
#     Hut_limits[key][number_type] = 'X'#*Hut_cross_sec

Hct_limits = json.loads(open(os.path.join(options.limitfolder, Hctjson)).read())
for key in Hct_limits:
  for number_type in Hct_limits[key]:
    if isinstance(Hct_limits[key][number_type], list):
      Hct_limits[key][number_type][0] = round(Hct_limits[key][number_type][0]*signal_Xsec_couplingOne['Hct'], 4)
      Hct_limits[key][number_type][1] = round(Hct_limits[key][number_type][1]*signal_Xsec_couplingOne['Hct'], 4)
    else:
      Hct_limits[key][number_type] = round(Hct_limits[key][number_type]*signal_Xsec_couplingOne['Hct'], 4)
#   if number_type == 'observed':
#     Hct_limits[key][number_type] = 'X'#*Hct_cross_sec

x_coup_exp, y_coup_exp = array( 'd' ), array( 'd' )
x_coup_obs, y_coup_obs = array( 'd' ), array( 'd' )
x_coup_one_up, x_coup_one_dn = array( 'd' ), array( 'd' )
y_coup_one_up, y_coup_one_dn = array( 'd' ), array( 'd' )
x_coup_two_up, x_coup_two_dn = array( 'd' ), array( 'd' )
y_coup_two_up, y_coup_two_dn = array( 'd' ), array( 'd' )
x_br_exp, y_br_exp = array( 'd' ), array( 'd' )
x_br_obs, y_br_obs = array( 'd' ), array( 'd' )
x_br_one_up, x_br_one_dn = array( 'd' ), array( 'd' )
y_br_one_up, y_br_one_dn = array( 'd' ), array( 'd' )
x_br_two_up, x_br_two_dn = array( 'd' ), array( 'd' )
y_br_two_up, y_br_two_dn = array( 'd' ), array( 'd' )

Hut_exp = Hut_limits[options.category]['expected']
Hut_obs = Hut_limits[options.category]['observed']
Hut_one_up = Hut_limits[options.category]['one_sigma'][1]
Hut_one_dn = Hut_limits[options.category]['one_sigma'][0]
Hut_two_up = Hut_limits[options.category]['two_sigma'][1]
Hut_two_dn = Hut_limits[options.category]['two_sigma'][0]

Hct_exp = Hct_limits[options.category]['expected']
Hct_obs = Hct_limits[options.category]['observed']
Hct_one_up = Hct_limits[options.category]['one_sigma'][1]
Hct_one_dn = Hct_limits[options.category]['one_sigma'][0]
Hct_two_up = Hct_limits[options.category]['two_sigma'][1]
Hct_two_dn = Hct_limits[options.category]['two_sigma'][0]

def coupl(Hut_limit, Hct_limit, pos, arrX, arrY):
  if pos <= sqrt(Hut_limit/signal_Xsec_couplingOneForBR['Hut']):
    coupling = sqrt(Hct_limit/signal_Xsec_couplingOneForBR['Hct']) * sqrt(1-pow(pos/sqrt(Hut_limit/signal_Xsec_couplingOneForBR['Hut']), 2))
    arrX.append(pos)
    arrY.append(coupling)

def br(Hut_limit, Hct_limit, pos, arrX, arrY):
  if 0.19 * pow(pos, 2) / 1.32158 <= 0.19 * Hut_limit / (signal_Xsec_couplingOneForBR['Hut'] * 1.32158):
    coupling = sqrt(Hct_limit/signal_Xsec_couplingOneForBR['Hct']) * sqrt(1-pow(pos/sqrt(Hut_limit/signal_Xsec_couplingOneForBR['Hut']), 2))
    br_x = 0.19 * pow(pos, 2) / 1.32158
    br_y = 0.19 * pow(coupling, 2) / 1.32158
    arrX.append(100 * br_x)
    arrY.append(100 * br_y)
    #arrX.append(br_x)
    #arrY.append(br_y)


for i in xrange(20000):
  x_pos = 0.00001 * i
  coupl(Hut_exp, Hct_exp, x_pos, x_coup_exp, y_coup_exp)
  coupl(Hut_obs, Hct_obs, x_pos, x_coup_obs, y_coup_obs)
  coupl(Hut_one_up, Hct_one_up, x_pos, x_coup_one_up, y_coup_one_up)
  coupl(Hut_one_dn, Hct_one_dn, x_pos, x_coup_one_dn, y_coup_one_dn)
  coupl(Hut_two_up, Hct_two_up, x_pos, x_coup_two_up, y_coup_two_up)
  coupl(Hut_two_dn, Hct_two_dn, x_pos, x_coup_two_dn, y_coup_two_dn)

  br(Hut_exp, Hct_exp, x_pos, x_br_exp, y_br_exp)
  br(Hut_obs, Hct_obs, x_pos, x_br_obs, y_br_obs)
  br(Hut_one_up, Hct_one_up, x_pos, x_br_one_up, y_br_one_up)
  br(Hut_one_dn, Hct_one_dn, x_pos, x_br_one_dn, y_br_one_dn)
  br(Hut_two_up, Hct_two_up, x_pos, x_br_two_up, y_br_two_up)
  br(Hut_two_dn, Hct_two_dn, x_pos, x_br_two_dn, y_br_two_dn)


# Create Canvas
c1 = TCanvas("c1","extrapolate",450,400)
p1 = c1.DrawFrame(0, 0.001, 0.15, 0.15)


# Create TGraph
g_coup_exp = TGraph(len(x_coup_exp), x_coup_exp, y_coup_exp)
g_coup_obs = TGraph(len(x_coup_obs), x_coup_obs, y_coup_obs)
print 'Hut obs kappa ',  x_coup_obs[-1], 'Hct obs kappa', y_coup_obs[0]
print 'Hut exp kappa ',  x_coup_exp[-1], 'Hct exp kappa', y_coup_exp[0]
#g_coup_one_up = TGraph(len(x_coup_one_up), x_coup_one_up, y_coup_one_up)
#g_coup_one_dn = TGraph(len(x_coup_one_dn), x_coup_one_dn, y_coup_one_dn)
#g_coup_two_up = TGraph(len(x_coup_two_up), x_coup_two_up, y_coup_two_up)
#g_coup_two_dn = TGraph(len(x_coup_two_dn), x_coup_two_dn, y_coup_two_dn)

g_coup_one_band = TGraph(len(x_coup_one_up)+len(x_coup_one_dn))
for i in xrange(len(x_coup_one_up)):
  g_coup_one_band.SetPoint(i, x_coup_one_up[i], y_coup_one_up[i]);
  if len(x_coup_one_up) + i < len(x_coup_one_up)+len(x_coup_one_dn):
    g_coup_one_band.SetPoint(len(x_coup_one_up) + i , x_coup_one_dn[len(x_coup_one_dn)-i-1], y_coup_one_dn[len(x_coup_one_dn)-i-1]);

g_coup_two_band = TGraph(len(x_coup_two_up)+len(x_coup_two_dn))
for i in xrange(len(x_coup_two_up)):
  g_coup_two_band.SetPoint(i, x_coup_two_up[i], y_coup_two_up[i]);
  if len(x_coup_two_up) + i < len(x_coup_two_up)+len(x_coup_two_dn):
    g_coup_two_band.SetPoint(len(x_coup_two_up) + i , x_coup_two_dn[len(x_coup_two_dn)-i-1], y_coup_two_dn[len(x_coup_two_dn)-i-1]);


# Change style
g_coup_exp.SetLineWidth(3)
g_coup_exp.SetLineStyle(7)
g_coup_obs.SetLineWidth(3)
g_coup_obs.SetLineColor(2)
if not options.unblind:
  g_coup_obs.SetLineColorAlpha(kRed, 0.0);
#g_coup_one_up.SetLineWidth(5)
#g_coup_one_dn.SetLineWidth(5)
#g_coup_two_up.SetLineWidth(5)
#g_coup_two_dn.SetLineWidth(5)
g_coup_one_band.SetFillColor(3)
g_coup_one_band.SetLineColor(3)
g_coup_two_band.SetFillColor(5)
g_coup_two_band.SetLineColor(5)


# Axis style
xAxis = p1.GetXaxis()
xAxis.SetTitle("#kappa_{Hut}")
xAxis.SetLabelSize(0.04)
xAxis.SetLabelFont(42)
xAxis.SetTitleFont(42)
xAxis.SetTitleOffset(1.0)
xAxis.SetTitleSize(0.05)
yAxis = p1.GetYaxis()
yAxis.SetTitle("#kappa_{Hct}")
yAxis.SetLabelSize(0.04)
yAxis.SetLabelFont(42)
yAxis.SetTitleFont(42)
yAxis.SetTitleOffset(1.3)
yAxis.SetTitleSize(0.05)


# Some text
progress = 'Preliminary'
latexLabel = TLatex()
latexLabel.SetTextSize(0.75 * c1.GetTopMargin())
latexLabel.SetNDC()
latexLabel.SetTextFont(42) # helvetica
latexLabel.DrawLatex(0.69, 0.96, '%s fb^{-1} (13 TeV)'%(options.lumi))
latexLabel.SetTextFont(61) # helvetica bold face
#latexLabel.SetTextSize(1.15 * c1.GetTopMargin())
#latexLabel.DrawLatex(0.78, 0.85, 'Hct')
latexLabel.SetTextSize(0.75 * c1.GetTopMargin())
latexLabel.DrawLatex(0.13, 0.96, "CMS")
#latexLabel.DrawLatex(0.14, 0.96, "CMS")
latexLabel.SetTextFont(52) # helvetica italics
if options.pas: latexLabel.DrawLatex(0.22, 0.96, progress)
latexLabel.Clear()


# Legend
legend = TLegend(0.55, 0.75, 0.9, 0.9, "95% CL upper limits")
legend.SetTextFont(42)
legend.SetTextSize(0.035)
legend.SetFillStyle(0)
legend.SetFillColor(kWhite)
legend.SetLineColor(kWhite)
legend.SetShadowColor(kWhite)
legend.AddEntry(g_coup_exp, 'Expected', 'l')
legend.AddEntry(g_coup_one_band, 'Expected #pm 1 std. dev.', 'f')
legend.AddEntry(g_coup_two_band, 'Expected #pm 2 std. dev.', 'f')
legend.AddEntry(g_coup_obs, 'Observed', 'l')


# Draw
g_coup_exp.Draw("c")
#g_coup_one_up.Draw("c same")
#g_coup_one_dn.Draw("c same")
#g_coup_two_up.Draw("c same")
#g_coup_two_dn.Draw("c same")
g_coup_two_band.Draw("f same")
g_coup_one_band.Draw("f same")
g_coup_obs.Draw("c same")
g_coup_exp.Draw("c same")
gPad.RedrawAxis();
legend.Draw('same')
c1.cd()
if options.pas: c1.Print(options.limitfolder + "/interpolated_coupling"+postfix+"_pas.pdf")
else:           c1.Print(options.limitfolder + "/interpolated_coupling"+postfix+".pdf")

#####################################################
c2 = TCanvas("c2","extrapolate",450,400)
p2 = c2.DrawFrame(0, 0.001, 0.25, 0.25)
#p2 = c2.DrawFrame(0, 0.00001, 0.0021, 0.0017)
#TGaxis.SetMaxDigits(2)
#TGaxis.SetExponentOffset(-0.03, -0.04, "x");
#TGaxis.SetExponentOffset(-0.07, 0.0, "y");

# Create TGraph
g_br_exp = TGraph(len(x_br_exp), x_br_exp, y_br_exp)
g_br_obs = TGraph(len(x_br_obs), x_br_obs, y_br_obs)
#g_br_one_up = TGraph(len(x_br_one_up), x_br_one_up, y_br_one_up)
#g_br_one_dn = TGraph(len(x_br_one_dn), x_br_one_dn, y_br_one_dn)
#g_br_two_up = TGraph(len(x_br_two_up), x_br_two_up, y_br_two_up)
#g_br_two_dn = TGraph(len(x_br_two_dn), x_br_two_dn, y_br_two_dn)


g_br_one_band = TGraph(len(x_br_one_up)+len(x_br_one_dn))
for i in xrange(len(x_br_one_up)):
  g_br_one_band.SetPoint(i, x_br_one_up[i], y_br_one_up[i]);
  if len(x_br_one_up) + i < len(x_br_one_up)+len(x_br_one_dn):
    g_br_one_band.SetPoint(len(x_br_one_up) + i , x_br_one_dn[len(x_br_one_dn)-i-1], y_br_one_dn[len(x_br_one_dn)-i-1]);

g_br_two_band = TGraph(len(x_br_two_up)+len(x_br_two_dn))
for i in xrange(len(x_br_two_up)):
  g_br_two_band.SetPoint(i, x_br_two_up[i], y_br_two_up[i]);
  if len(x_br_two_up) + i < len(x_br_two_up)+len(x_br_two_dn):
    g_br_two_band.SetPoint(len(x_br_two_up) + i , x_br_two_dn[len(x_br_two_dn)-i-1], y_br_two_dn[len(x_br_two_dn)-i-1]);

# Change style
g_br_exp.SetLineWidth(3)
g_br_exp.SetLineStyle(7)
g_br_obs.SetLineWidth(3)
g_br_obs.SetLineColor(2)
if not options.unblind:
  g_br_obs.SetLineColorAlpha(kRed, 0.0);
#g_br_one_up.SetLineWidth(5)
#g_br_one_dn.SetLineWidth(5)
#g_br_two_up.SetLineWidth(5)
#g_br_two_dn.SetLineWidth(5)
g_br_one_band.SetFillColor(3)
g_br_one_band.SetLineColor(3)
g_br_two_band.SetFillColor(5)
g_br_two_band.SetLineColor(5)


# Axis style
xAxis = p2.GetXaxis()
#xAxis.SetTitle("BR_{Hut}[%]")
xAxis.SetTitle("B(t#rightarrow Hu) (%)")
xAxis.SetLabelSize(0.04)
xAxis.SetLabelFont(42)
xAxis.SetTitleFont(42)
xAxis.SetTitleOffset(1.0)
xAxis.SetTitleSize(0.05)
yAxis = p2.GetYaxis()
#yAxis.SetTitle("BR_{Hct}[%]")
yAxis.SetTitle("B(t#rightarrow Hc) (%)")
yAxis.SetLabelSize(0.04)
yAxis.SetLabelFont(42)
yAxis.SetTitleFont(42)
yAxis.SetTitleOffset(1.3)
yAxis.SetTitleSize(0.05)


# Some text
progress = 'Preliminary'
latexLabel = TLatex()
latexLabel.SetTextSize(0.75 * c1.GetTopMargin())
latexLabel.SetNDC()
latexLabel.SetTextFont(42) # helvetica
latexLabel.DrawLatex(0.69, 0.96, '%s fb^{-1} (13 TeV)'%(options.lumi))
latexLabel.SetTextFont(61) # helvetica bold face
#latexLabel.SetTextSize(1.15 * c1.GetTopMargin())
#latexLabel.DrawLatex(0.78, 0.85, 'Hct')
latexLabel.SetTextSize(0.75 * c1.GetTopMargin())
latexLabel.DrawLatex(0.13, 0.96, "CMS")
#latexLabel.DrawLatex(0.14, 0.96, "CMS")
latexLabel.SetTextFont(52) # helvetica italics
if options.pas: latexLabel.DrawLatex(0.22, 0.96, progress)
latexLabel.Clear()


# Draw
g_br_exp.Draw("c")
#g_br_one_up.Draw("c same")
#g_br_one_dn.Draw("c same")
#g_br_two_up.Draw("c same")
#g_br_two_dn.Draw("c same")
g_br_two_band.Draw("f same")
g_br_one_band.Draw("f same")
g_br_obs.Draw("c same")
g_br_exp.Draw("c same")
gPad.RedrawAxis();
legend.Draw('same')

if options.pas: c2.Print(options.limitfolder + "/interpolated_br"+postfix+"_pas.pdf")
else:           c2.Print(options.limitfolder + "/interpolated_br"+postfix+".pdf")
