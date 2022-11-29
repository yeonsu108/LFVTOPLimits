import json, sys, os
import numpy as np
import math

limitfolder = sys.argv[1]


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

def calcBr(op, limits):
    out = []
    if op == "cs" or op == "us":
        out = 2*np.array(limits)*(172.5**5)*10**(-6)/(6144*(math.pi**3))
    elif op == "cv" or op == "uv":
        out = np.array(limits)*(172.5**5)*10**(-6)/(1536*(math.pi**3))
    elif op == "ct" or op == "ut":
        out = 2*np.array(limits)*(172.5**5)*10**(-6)/(128*(math.pi**3))
    out = list(np.around(out,decimals=3))
    if len(out)==1: result = str(out[0])
    else: result = str(out)
    return result



################
for signal in ['st_lfv_cs', 'st_lfv_cv', 'st_lfv_ct', 'st_lfv_us', 'st_lfv_uv', 'st_lfv_ut']:
	op = signal.split("_")[2]
	limits = json.loads(open(os.path.join(limitfolder, 'st_lfv_'+op+'_limits.json')).read())
	limits = limits[""]
	print(signal , op)
	print(" & ".join([calcXsec(signal,[limits['expected']]),calcWilson([limits['expected']]),calcBr(op, [limits['expected']])]))
	print("\\\\")
	print(" & & ")
	print(" & ".join([calcXsec(signal,limits['one_sigma']),calcWilson(limits['one_sigma']),calcBr(op, limits['one_sigma'])]))
	print("\\cline{3-6} ")




