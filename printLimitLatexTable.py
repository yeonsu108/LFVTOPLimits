import json, sys, os
import numpy as np
import math

limitfolder = sys.argv[1]
year = limitfolder.split("_")[-1:]

signal_Xsec = {'st_lfv_cs':10.09,'st_lfv_cv':58.3,'st_lfv_ct':307.4,'st_lfv_us':86.49,'st_lfv_uv':414.5,'st_lfv_ut':1925}  # for limit rescaling if the signal Xsec inseted in combine was not 1 pb

def calcXsec(signal,limits):
    xsec= list(np.around(np.array(limits) * signal_Xsec[signal],decimals=3))
    if len(xsec)==1: result = str(xsec[0])
    else: result = str(xsec)
    return result

def calcWilson(limits):
    wilson = list(np.around(np.sqrt(limits),decimals=3))
    if len(wilson)==1: result = str(wilson[0])
    else: result = str(wilson)
    return result


#Add /1.3 for top width 
def calcBr(op, limits):
    out = []
    if op == "cs" or op == "us":
        out = 2*np.array(limits)*(172.5**5)*10**(-6)/(1.3*6144*(math.pi**3))
    elif op == "cv" or op == "uv":
        out = 4*np.array(limits)*(172.5**5)*10**(-6)/(1.3*1536*(math.pi**3))
    elif op == "ct" or op == "ut":
        out = 2*np.array(limits)*(172.5**5)*10**(-6)/(1.3*128*(math.pi**3))
    out = list(np.around(out,decimals=3))
    if len(out)==1: result = str(out[0])
    else: result = str(out)
    return result

################
for_table = []
for signal in ['st_lfv_cs', 'st_lfv_cv', 'st_lfv_ct', 'st_lfv_us', 'st_lfv_uv', 'st_lfv_ut']:
#for signal in ['st_lfv_cs']: #, 'st_lfv_cv', 'st_lfv_ct', 'st_lfv_us', 'st_lfv_uv', 'st_lfv_ut']:
	op = signal.split("_")[2]
	limits = json.loads(open(os.path.join(limitfolder, 'st_lfv_'+op+'_limits.json')).read())
	limits = limits[""]
	print(signal , op)
	nom = " & ".join([calcXsec(signal,[limits['expected']]),calcWilson([limits['expected']]),calcBr(op, [limits['expected']])])
	print("nom : ", nom)
	for_table.append(nom)
	unc = " & ".join([calcXsec(signal,limits['one_sigma']),calcWilson(limits['one_sigma']),calcBr(op, limits['one_sigma'])]) 
	print("unc : ", unc)
	for_table.append(unc)

#print(len(for_table),for_table)


lfv_table = """
\\begin{{table}}[!hp] 
    \\centering 
    \\renewcommand{{\\arraystretch}}{{1.1}}
    \\begin{{tabular}}{{c|c|c|c|c|c}} 
        \\hline\\hline 
        Category & Interaction & Type & $\\sigma$ [fb] & $C_{{tq\\mu\\tau}}\\slash\\Lambda^{{2}}$ [$TeV^{{-2}}$] & $Br(t\\to q\\mu\\tau)\\times 10^{{-6}}$ \\\\ \\hline\\hline
        \\multirow{{12}}{{*}}{{Combined}} & \\multirow{{6}}{{*}}{{$tc\\mu\\tau$}}  & \\multirow{{2}}{{*}}{{Scalar}} &
        {lim0}\\\\& & & {lim1}\\\\\\cline{{3-6}} 
         & & \\multirow{{2}}{{*}}{{Vector}} & {lim2}\\\\ & & & {lim3}\\\\\\cline{{3-6}} 
         & & \\multirow{{2}}{{*}}{{Tensor}} & {lim4}\\\\ & & & {lim5}\\\\\\cline{{2-6}} 
         & \\multirow{{6}}{{*}}{{$tu\\mu\\tau$}} & \\multirow{{2}}{{*}}{{Scalar}}
        &  {lim6}\\\\ & & & {lim7}\\\\\\cline{{3-6}} 
         & & \\multirow{{2}}{{*}}{{Vector}} & {lim8}\\\\ & & & {lim9}\\\\\\cline{{3-6}} 
         & & \\multirow{{2}}{{*}}{{Tensor}} &{lim10}\\\\ & & & {lim11}\\\\\\cline{{3-6}} 
        \\hline\\hline
    \\end{{tabular}}
    \\caption{{Table for Run {year} upper limits of LFV cross section ($\\sigma$), Wilson Coefficient ($C_{{tq\\mu\\tau}}$), and branching fraction for different types of interactions. $\\pm1\\sigma$ values are in brackets.}} 
    \\label{{tab:run2limit}} 
\\end{{table}}
""".format(
lim0=for_table[0],
lim1=for_table[1],
lim2=for_table[2],
lim3=for_table[3],
lim4=for_table[4],
lim5=for_table[5],
lim6=for_table[6],
lim7=for_table[7],
lim8=for_table[8],
lim9=for_table[9],
lim10=for_table[10],
lim11=for_table[11],
year = year)
print(lfv_table)



