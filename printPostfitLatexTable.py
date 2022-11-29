import sys, os, re
import numpy as np
from math import sqrt
from ROOT import *
import ROOT

limitfolder = sys.argv[1]
couplings = ['Hct']

if len(sys.argv) > 2: years = sys.argv[2]
else: years = ''

for coupling in couplings:

    nums = {}
    for process in ['data_obs', 'ttbb', 'ttcc', 'ttlf', 'other', 'qcd', 'TotalBkg']:
        rootfolder = os.path.join(limitfolder, coupling + '/postfit_shapes_FCNC_'+coupling+'_Discriminant_DNN_'+coupling+'_all_forPlotIt')
        if len(years) > 1:
            rootfolder = os.path.join(limitfolder, coupling + '/postfit_shapes_FCNC_'+coupling+'_Discriminant_DNN_'+coupling+'_'+years+'_all_forPlotIt')
        f_tmp = TFile.Open(os.path.join(rootfolder, process + '_postfit_histos.root'))

        for cat in ['b2j4']:
            hname = 'DNN_'+coupling+'_'+cat
            if cat != 'b2j3' and process == 'qcd': pass
            else:
                nums[cat+process] = f_tmp.Get(hname).Integral()
                if any(i in process for i in ['data_obs']): pass
                else:
                    nums[cat+process+'Unc'] = float(np.format_float_positional(0.5*(abs(f_tmp.Get(hname+'__postfitup').Integral()-f_tmp.Get(hname).Integral())+abs(f_tmp.Get(hname+'__postfitdown').Integral()-f_tmp.Get(hname).Integral())), precision=2, unique=False, fractional=False, trim='k'))

    print(8*"*")
    print(nums)
    print(8*"*")

    table = """
    \\begin{{tabular}}{{ccrclcrclcrclcrclcrcl}}
      \hline
      Category  & & \\multicolumn{{3}}{{c}}{{b2j4}} & & \\multicolumn{{3}}{{c}}{{b2j4}} & & \\multicolumn{{3}}{{c}}{{b2j4}} & & \\multicolumn{{3}}{{c}}{{b2j4}} & & \\multicolumn{{3}}{{c}}{{b2j4}} \\\\ \hline
      Data      & & \\multicolumn{{3}}{{c}}{{ {b2j4data:8.0f} }} & & \\multicolumn{{3}}{{c}}{{ {b2j4data:8.0f} }} & & \\multicolumn{{3}}{{c}}{{ {b2j4data:8.0f} }} & & \\multicolumn{{3}}{{c}}{{ {b2j4data:8.0f} }} & & \\multicolumn{{3}}{{c}}{{ {b2j4data:8.0f} }} \\\\ [1mm]
      \\ttbb     & & {b2j4ttbb:8.0f} & $\pm$ & {b2j4ttbbUnc:5.0f} & & {b2j4ttbb:8.0f} & $\pm$ & {b2j4ttbbUnc:5.0f} & & {b2j4ttbb:8.0f} & $\pm$ & {b2j4ttbbUnc:5.0f} & & {b2j4ttbb:8.0f} & $\pm$ & {b2j4ttbbUnc:5.0f} & & {b2j4ttbb:8.0f} & $\pm$ & {b2j4ttbbUnc:5.0f} \\\\
      \\ttcc     & & {b2j4ttcc:8.0f} & $\pm$ & {b2j4ttccUnc:5.0f} & & {b2j4ttcc:8.0f} & $\pm$ & {b2j4ttccUnc:5.0f} & & {b2j4ttcc:8.0f} & $\pm$ & {b2j4ttccUnc:5.0f} & & {b2j4ttcc:8.0f} & $\pm$ & {b2j4ttccUnc:5.0f} & & {b2j4ttcc:8.0f} & $\pm$ & {b2j4ttccUnc:5.0f} \\\\
      \\ttbar LF & & {b2j4ttlf:8.0f} & $\pm$ & {b2j4ttlfUnc:5.0f} & & {b2j4ttlf:8.0f} & $\pm$ & {b2j4ttlfUnc:5.0f} & & {b2j4ttlf:8.0f} & $\pm$ & {b2j4ttlfUnc:5.0f} & & {b2j4ttlf:8.0f} & $\pm$ & {b2j4ttlfUnc:5.0f} & & {b2j4ttlf:8.0f} & $\pm$ & {b2j4ttlfUnc:5.0f} \\\\
      Other     & & {b2j4other:8.0f} & $\pm$ & {b2j4otherUnc:5.0f} & & {b2j4other:8.0f} & $\pm$ & {b2j4otherUnc:5.0f} & & {b2j4other:8.0f} & $\pm$ & {b2j4otherUnc:5.0f} & & {b2j4other:8.0f} & $\pm$ & {b2j4otherUnc:5.0f} & & {b2j4other:8.0f} & $\pm$ & {b2j4otherUnc:5.0f} \\\\
      QCD       & & {b2j4qcd:8.0f} & $\pm$ & {b2j4qcdUnc} & & & {b2j4qcd} & & & & {b2j4qcd} & & & & {b2j4qcd} & & & & {b2j4qcd} & \\\\ [1mm]
      Total     & & {b2j4total:8.0f} & $\pm$ & {b2j4totalUnc} & & {b2j4total:8.0f} & $\pm$ & {b2j4totalUnc} & & {b2j4total:8.0f} & $\pm$ & {b2j4totalUnc} & & {b2j4total:8.0f} & $\pm$ & {b2j4totalUnc} & & {b2j4total:8.0f} & $\pm$ & {b2j4totalUnc} \\\\ \hline
   \end{{tabular}}
    """.format(
        b2j4data=nums['b2j4data_obs'],
        b2j4ttbb=nums['b2j4ttbb'], 
        b2j4ttcc=nums['b2j4ttcc'], 
        b2j4ttlf=nums['b2j4ttlf'], 
        b2j4other=nums['b2j4other'],
        b2j4qcd='\\NA',
        b2j4total=nums['b2j4TotalBkg'],
        b2j4ttbbUnc=nums['b2j4ttbbUnc'],
        b2j4ttccUnc=nums['b2j4ttccUnc'],
        b2j4ttlfUnc=nums['b2j4ttlfUnc'],
        b2j4otherUnc=nums['b2j4otherUnc'],
        b2j4qcdUnc='\\NA',
        b2j4totalUnc='100',
        )
    print coupling + ':'
    print table

    table = re.sub(" \d{5} ", lambda m: str(' ' + m.group().rstrip(' ').lstrip(' ')[0:2] + '\,' + m.group().rstrip(' ').lstrip(' ')[2:] + ' '), table)
    table = re.sub(" \d{6} ", lambda m: str(' ' + m.group().rstrip(' ').lstrip(' ')[0:3] + '\,' + m.group().rstrip(' ').lstrip(' ')[3:] + ' '), table)
    table = re.sub(" \d{7} ", lambda m: str(' ' + m.group().rstrip(' ').lstrip(' ')[0:1] + '\,' + m.group().rstrip(' ').lstrip(' ')[1:4] + '\,' + m.group().rstrip(' ').lstrip(' ')[4:] + ' '), table)
    table = re.sub(" \d{8} ", lambda m: str(' ' + m.group().rstrip(' ').lstrip(' ')[0:2] + '\,' + m.group().rstrip(' ').lstrip(' ')[2:5] + '\,' + m.group().rstrip(' ').lstrip(' ')[5:] + ' '), table)
    print table

    table_filename = os.path.join(limitfolder, coupling + "_postfit_table.tex")
    with open(table_filename, 'w') as table_file:
        table_file.write(table)
