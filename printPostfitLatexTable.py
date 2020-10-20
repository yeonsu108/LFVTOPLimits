import sys, os
from math import sqrt
from ROOT import *
import ROOT

limitfolder = sys.argv[1]
couplings = ['Hut','Hct']

for coupling in couplings:

    nums = {}
    for process in ['data_obs', 'ttbb', 'ttcc', 'ttlf', 'other', 'qcd', 'TotalBkg']:
        rootfolder = os.path.join(limitfolder, coupling + '/postfit_shapes_FCNC_'+coupling+'_Discriminant_DNN_'+coupling+'_all_forPlotIt')
        f_tmp = TFile.Open(os.path.join(rootfolder, process + '_postfit_histos.root'))

        for cat in ['b2j3', 'b2j4', 'b3j3', 'b3j4', 'b4j4']:
            hname = 'DNN_'+coupling+'_'+cat
            if cat != 'b2j3' and process == 'qcd': pass
            else:
                nums[cat+process] = f_tmp.Get(hname).Integral()
                if any(i in process for i in ['data_obs', 'TotalBkg']): pass
                else:
                    nums[cat+process+'Unc'] = 0.5*(abs(f_tmp.Get(hname+'__postfitup').Integral()-f_tmp.Get(hname).Integral())+abs(f_tmp.Get(hname+'__postfitdown').Integral()-f_tmp.Get(hname).Integral()))

    for cat in ['b2j3', 'b2j4', 'b3j3', 'b3j4', 'b4j4']:
        if cat == 'b2j3': nums[cat+'TotalBkgUnc'] = sqrt(nums[cat+'ttbbUnc']**2 + nums[cat+'ttccUnc']**2 + nums[cat+'ttlfUnc']**2 + nums[cat+'otherUnc']**2 + nums[cat+'qcdUnc']**2)
        else: nums[cat+'TotalBkgUnc'] = sqrt(nums[cat+'ttbbUnc']**2 + nums[cat+'ttccUnc']**2 + nums[cat+'ttlfUnc']**2 + nums[cat+'otherUnc']**2)


#QCD       & {b2j3qcd:8.0f} $\pm$ {b2j3qcdUnc:5.0f} & {b2j4qcd:>20} & {b3j3qcd:>20} & {b3j4qcd:>20} & {b4j4qcd:>20} \\\\ \hline
#QCD       & {b2j3qcd:>20} & {b2j4qcd:>20} & {b3j3qcd:>20} & {b3j4qcd:>20} & {b4j4qcd:>20} \\\\ \hline

    table = """
    \\begin{{tabular}}{{|l|c|c|c|c|c|}}
      \hline
      Category  & b2j3 & b2j4 & b3j3 & b3j4 & b4j4 \\\\ \hline
      Data      & {b2j3data:8.0f} & {b2j4data:8.0f} & {b3j3data:8.0f} & {b3j4data:8.0f} & {b4j4data:8.0f} \\\\ \hline
      \\ttbb     & {b2j3ttbb:8.0f} $\pm$ {b2j3ttbbUnc:5.0f} & {b2j4ttbb:8.0f} $\pm$ {b2j4ttbbUnc:5.0f} & {b3j3ttbb:8.0f} $\pm$ {b3j3ttbbUnc:5.0f} & {b3j4ttbb:8.0f} $\pm$ {b3j4ttbbUnc:5.0f} & {b4j4ttbb:8.0f} $\pm$ {b4j4ttbbUnc:5.0f} \\\\
      \\ttcc     & {b2j3ttcc:8.0f} $\pm$ {b2j3ttccUnc:5.0f} & {b2j4ttcc:8.0f} $\pm$ {b2j4ttccUnc:5.0f} & {b3j3ttcc:8.0f} $\pm$ {b3j3ttccUnc:5.0f} & {b3j4ttcc:8.0f} $\pm$ {b3j4ttccUnc:5.0f} & {b4j4ttcc:8.0f} $\pm$ {b4j4ttccUnc:5.0f} \\\\
      \\ttbar LF & {b2j3ttlf:8.0f} $\pm$ {b2j3ttlfUnc:5.0f} & {b2j4ttlf:8.0f} $\pm$ {b2j4ttlfUnc:5.0f} & {b3j3ttlf:8.0f} $\pm$ {b3j3ttlfUnc:5.0f} & {b3j4ttlf:8.0f} $\pm$ {b3j4ttlfUnc:5.0f} & {b4j4ttlf:8.0f} $\pm$ {b4j4ttlfUnc:5.0f} \\\\
      Other     & {b2j3other:8.0f} $\pm$ {b2j3otherUnc:5.0f} & {b2j4other:8.0f} $\pm$ {b2j4otherUnc:5.0f} & {b3j3other:8.0f} $\pm$ {b3j3otherUnc:5.0f} & {b3j4other:8.0f} $\pm$ {b3j4otherUnc:5.0f} & {b4j4other:8.0f} $\pm$ {b4j4otherUnc:5.0f} \\\\
      QCD       & {b2j3qcd:8.0f} $\pm$ {b2j3qcdUnc:5.0f} & {b2j4qcd:>20} & {b3j3qcd:>20} & {b3j4qcd:>20} & {b4j4qcd:>20} \\\\ \hline
      Total     & {b2j3total:8.0f} $\pm$ {b2j3totalUnc:5.0f} & {b2j4total:8.0f} $\pm$ {b2j4totalUnc:5.0f} & {b3j3total:8.0f} $\pm$ {b3j3totalUnc:5.0f} & {b3j4total:8.0f} $\pm$ {b3j4totalUnc:5.0f} & {b4j4total:8.0f} $\pm$ {b4j4totalUnc:5.0f} \\\\ \hline
   \end{{tabular}}
    """.format(
        b2j3data=nums['b2j3data_obs'], b2j4data=nums['b2j4data_obs'], b3j3data=nums['b3j3data_obs'], b3j4data=nums['b3j4data_obs'], b4j4data=nums['b4j4data_obs'],
        b2j3ttbb=nums['b2j3ttbb'], b2j4ttbb=nums['b2j4ttbb'], b3j3ttbb=nums['b3j3ttbb'], b3j4ttbb=nums['b3j4ttbb'], b4j4ttbb=nums['b4j4ttbb'],
        b2j3ttcc=nums['b2j3ttcc'], b2j4ttcc=nums['b2j4ttcc'], b3j3ttcc=nums['b3j3ttcc'], b3j4ttcc=nums['b3j4ttcc'], b4j4ttcc=nums['b4j4ttcc'],
        b2j3ttlf=nums['b2j3ttlf'], b2j4ttlf=nums['b2j4ttlf'], b3j3ttlf=nums['b3j3ttlf'], b3j4ttlf=nums['b3j4ttlf'], b4j4ttlf=nums['b4j4ttlf'],
        b2j3other=nums['b2j3other'], b2j4other=nums['b2j4other'], b3j3other=nums['b3j3other'], b3j4other=nums['b3j4other'], b4j4other=nums['b4j4other'],
        b2j3qcd=nums['b2j3qcd'], b2j4qcd='-', b3j3qcd='-', b3j4qcd='-', b4j4qcd='-',
        b2j3total=nums['b2j3TotalBkg'], b2j4total=nums['b2j4TotalBkg'], b3j3total=nums['b3j3TotalBkg'], b3j4total=nums['b3j4TotalBkg'], b4j4total=nums['b4j4TotalBkg'],
        b2j3ttbbUnc=nums['b2j3ttbbUnc'], b2j4ttbbUnc=nums['b2j4ttbbUnc'], b3j3ttbbUnc=nums['b3j3ttbbUnc'], b3j4ttbbUnc=nums['b3j4ttbbUnc'], b4j4ttbbUnc=nums['b4j4ttbbUnc'],
        b2j3ttccUnc=nums['b2j3ttccUnc'], b2j4ttccUnc=nums['b2j4ttccUnc'], b3j3ttccUnc=nums['b3j3ttccUnc'], b3j4ttccUnc=nums['b3j4ttccUnc'], b4j4ttccUnc=nums['b4j4ttccUnc'],
        b2j3ttlfUnc=nums['b2j3ttlfUnc'], b2j4ttlfUnc=nums['b2j4ttlfUnc'], b3j3ttlfUnc=nums['b3j3ttlfUnc'], b3j4ttlfUnc=nums['b3j4ttlfUnc'], b4j4ttlfUnc=nums['b4j4ttlfUnc'],
        b2j3otherUnc=nums['b2j3otherUnc'], b2j4otherUnc=nums['b2j4otherUnc'], b3j3otherUnc=nums['b3j3otherUnc'], b3j4otherUnc=nums['b3j4otherUnc'], b4j4otherUnc=nums['b4j4otherUnc'],
        b2j3qcdUnc=nums['b2j3qcdUnc'],
        b2j3totalUnc=nums['b2j3TotalBkgUnc'], b2j4totalUnc=nums['b2j4TotalBkgUnc'], b3j3totalUnc=nums['b3j3TotalBkgUnc'], b3j4totalUnc=nums['b3j4TotalBkgUnc'], b4j4totalUnc=nums['b4j4TotalBkgUnc'],
        )
    table_filename = os.path.join(limitfolder, coupling + "_postfit_table.tex")
    with open(table_filename, 'w') as table_file:
        table_file.write(table)
    print coupling + ':'
    print table

