#! /bin/env python

# Python imports
import os, sys, stat, argparse, getpass, json
from datetime import datetime
from math import sqrt
import yaml
from collections import OrderedDict
from subprocess import call
import array

from symmetrize import smoothing, symmetrize

# to prevent pyroot to hijack argparse we need to go around
tmpargv = sys.argv[:] 
sys.argv = []

# ROOT imports
import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True
sys.argv = tmpargv

hadNegBinForProcess = {}
hadNegBinErrForProcess = {}
def setNegativeBinsToZero(h, process):
    if not process in hadNegBinForProcess:
        hadNegBinForProcess[process] = False
    for i in range(1, h.GetNbinsX() + 1):
        if h.GetBinContent(i) < 0.:
            if not hadNegBinForProcess[process]:
                print('Remove negative bin in TH1 %s for process %s'%(h.GetTitle(), process))
            hadNegBinForProcess[process] = True
            h.SetBinContent(i, 0.)
    
def get_hist_regex(r):
    return '^%s(__.*(up|down))?$' % r

cmssw_base = os.environ['CMSSW_BASE']

parser = argparse.ArgumentParser(description='Create shape datacards ready for combine')
parser.add_argument('-p', '--path', action='store', dest='root_path', type=str, default=cmssw_base+'/src/UserCode/FCNCLimits/histos_suitable_for_limits_200101_2017/training_0101010101', help='Directory containing rootfiles with the TH1 used for limit settings')
parser.add_argument('-l', '--luminosity', action='store', type=float, dest='luminosity', default=41529, help='Integrated luminosity (default is 41529 /pb)')
parser.add_argument('-o', '--output', action='store', dest='output', type=str, default='datacards_200101_2017', help='Output directory')
parser.add_argument('-applyxsec' , action='store', dest='applyxsec', type=bool, default=True, help='Reweight MC processes by Xsec/Nevt from yml config.')
parser.add_argument('-xsecfile' , action='store', dest='xsecfile', type=str, default='files_17.yml', help='YAML config file path with Xsec and Nevt.')
parser.add_argument('--nosys', action='store', dest='nosys', default=False, help='Consider or not systematic uncertainties (NB : bbb uncertainty is with another flag)')
parser.add_argument('--sysToAvoid', action='store', dest='sysToAvoid', nargs='+', default=['tauidjetHighptstat'], help='Set it to exclude some of the systematics. Name should as in rootfile without the up/dowm postfix, e.g. --sysToAvoid pu hf')
parser.add_argument('--sysForSMtt', action='store', dest='sysForSMtt', nargs='+', default=['isr','fsr', 'pdfalphas','mescale','renscale','facscale','tune','hdamp'], help='Systematics affecting only SM tt.')
parser.add_argument('--sysForSig', action='store', dest='sysForSig', nargs='+', default=['isr','fsr','mescale','renscale','facscale'], help='Systematics affecting Signals (must be common with SMtt)')
parser.add_argument('--correlatedSys', action='store', dest='correlatedSys', nargs='+', default=['muid', 'muiso', 'mutrg', 'pu', 'isr', 'fsr', 'pdfalphas', 'mescale', 'renscale', 'facscale', 'tune', 'hdamp', 'toppt'], help='Systematics that are correlated accross years. NB: cross section unc are added by hand at the end of this script, go there to change correlation for them.')
parser.add_argument('-dataYear' , action='store', dest='dataYear', type=str, default='2017', help='Which year were the data taken? This has to be added in datacard entries in view of combination (avoid considering e.g. correlated lumi uncertainty accross years)')

options = parser.parse_args()


scale_breakdown = ['mescalemu1ta1', 'mescalemu1ta2', 'mescalemu2ta1', 'mescalemu2ta2',
                   'renscalemu1ta1', 'renscalemu1ta2', 'renscalemu2ta1', 'renscalemu2ta2',
                   'facscalemu1ta1', 'facscalemu1ta2', 'facscalemu2ta1', 'facscalemu2ta2']

correlatedSys = options.correlatedSys
correlatedSys.extend(['jesAbsolute', 'jesAbsolute_'+options.dataYear, 'jesBBEC1', 'jesBBEC1_'+options.dataYear,
                      'jesFlavorQCD',
                      'jesFlavorPureGluon', 'jesFlavorPureQuark', 'jesFlavorPureCharm', 'jesFlavorPureBottom',
                      'jesRelativeBal', 'jesRelativeSample_'+options.dataYear, 'jesHEM'])

correlatedSys.extend(['btagcferr1','btagcferr2','btaghf','btaglf'])
correlatedSys.extend(['tauidjetHighptextrap','tauidjetHighptsyst','tauidjetSystalleras'])
correlatedSys.extend(scale_breakdown)
correlatedSys.extend(['pdf'+str(i) for i in range(1,101)])
correlatedSys.extend(['muhighpt', 'muonhighscale'])

options.sysToAvoid.extend(['muonhighscale', 'metUnclust'])

sysForSMtt = options.sysForSMtt
sysForSMtt.extend(scale_breakdown)
sysForSMtt.extend(['pdf'+str(i) for i in range(1,101)])

sysForSig = options.sysForSig
sysForSig.extend(scale_breakdown)
sysForSig.extend(['pdf'+str(i) for i in range(1,101)])


years = {'2016pre': 19502, '2016post': 16812, '2017': 41480, '2018':59832}
luminosity = years[options.dataYear]

individual_discriminants = { # support regex (allow to avoid ambiguities if many histogram contains same patterns)
        'DNN': get_hist_regex('h_dnn_pred_S5'),
        #Drawing input postfit - remove rebins, include scales, no need to draw all signals, run only cards for each year
        #'DNN': get_hist_regex('h_muon1_pt_S5'),
        #'DNN': get_hist_regex('h_tau1_pt_S5'),
        #'DNN': get_hist_regex('h_jet1_pt_S5'),
        #'DNN': get_hist_regex('h_jet2_pt_S5'),
        #'DNN': get_hist_regex('h_mutau_mass_S5'),
        }

discriminants = { # 'name of datacard' : list of tuple with (dicriminant ID, name in 'individual_discriminants' dictionary above). Make sure the 'name of datacard' ends with '_categoryName (for plot step)
    "DNN_st_lfv_cs" : [ (1, 'DNN')],
    "DNN_st_lfv_ct" : [ (1, 'DNN')],
    "DNN_st_lfv_cv" : [ (1, 'DNN')],
    "DNN_st_lfv_us" : [ (1, 'DNN')],
    "DNN_st_lfv_ut" : [ (1, 'DNN')],
    "DNN_st_lfv_uv" : [ (1, 'DNN')],
    #key does matter when removeing qcd-relavant discriminant below
    }

# IF you change Bkg Def, don't forget to change also the backgrounds list in main and the systematics for cross sections

processes_mapping = { # Dict with { key(human friendly name of your choice) : value(regex to find rootfile) }. Be carefull not to match too many files with the regex!
        # Note: no entries from, WJetsToLNu_HT0To100, WJetsToLNu_HT100To200, hist_ST_s
        'tt': ['hist_TTToSemiLeptonic.root','hist_TTTo2L2Nu.root'],
        'singleTop':['hist_ST_t_antitop_4f.root','hist_ST_t_top_4f.root','hist_ST_tW_antitop_5f.root','hist_ST_tW_top_5f.root'],
        'other' : ['hist_TTToHadronic.root',
                   'hist_WJetsToLNu_HT1200To2500.root', 'hist_WJetsToLNu_HT200To400.root', 'hist_WJetsToLNu_HT2500ToInf.root', 'hist_WJetsToLNu_HT400To600.root', 'hist_WJetsToLNu_HT600To800.root', 'hist_WJetsToLNu_HT800To1200.root',
                   'hist_WW.root','hist_WZ.root','hist_ZZ.root',
                   'hist_DYJetsToLL_M50_HT100to200.root','hist_DYJetsToLL_M50_HT1200to2500.root','hist_DYJetsToLL_M50_HT200to400.root','hist_DYJetsToLL_M50_HT2500toInf.root','hist_DYJetsToLL_M50_HT400to600.root','hist_DYJetsToLL_M50_HT600to800.root','hist_DYJetsToLL_M50_HT800to1200.root','hist_DYJetsToLL_M-10to50.root',
                   'hist_TTWJetsToLNu.root','hist_TTZToLLNuNu.root','hist_TTZToQQ.root','hist_ttHTobb.root','hist_ttHToNonbb.root'],
        # Signal
        'st_lfv_cs': ['hist_ST_LFV_TCMuTau_Scalar.root','hist_TT_LFV_TCMuTau_Scalar.root'],
        'st_lfv_ct': ['hist_ST_LFV_TCMuTau_Tensor.root','hist_TT_LFV_TCMuTau_Tensor.root'],
        'st_lfv_cv': ['hist_ST_LFV_TCMuTau_Vector.root','hist_TT_LFV_TCMuTau_Vector.root'],
        'st_lfv_us': ['hist_ST_LFV_TUMuTau_Scalar.root','hist_TT_LFV_TUMuTau_Scalar.root'],
        'st_lfv_ut': ['hist_ST_LFV_TUMuTau_Tensor.root','hist_TT_LFV_TUMuTau_Tensor.root'],
        'st_lfv_uv': ['hist_ST_LFV_TUMuTau_Vector.root','hist_TT_LFV_TUMuTau_Vector.root'],
        # Data
        'data_all' : ['hist_SingleMuon.root'],

        ###################
        # Old definitions #
        ###################
        #'wJets' : ['hist_WJetsToLNu_HT0To100.root', 'hist_WJetsToLNu_HT100To200.root', 'hist_WJetsToLNu_HT1200To2500.root', 'hist_WJetsToLNu_HT200To400.root', 'hist_WJetsToLNu_HT2500ToInf.root', 'hist_WJetsToLNu_HT400To600.root', 'hist_WJetsToLNu_HT600To800.root', 'hist_WJetsToLNu_HT800To1200.root'],
        #'wJets' : [ 'hist_WJetsToLNu_HT1200To2500.root', 'hist_WJetsToLNu_HT200To400.root', 'hist_WJetsToLNu_HT2500ToInf.root', 'hist_WJetsToLNu_HT400To600.root', 'hist_WJetsToLNu_HT600To800.root', 'hist_WJetsToLNu_HT800To1200.root'],
        #'vv' : ['hist_WW.root','hist_WZ.root','hist_ZZ.root'],
        #'DY' : ['hist_DYJetsToLL_M50_amc.root','hist_DYJetsToLL_M-10to50.root'],
        #'TTX' : ['hist_TTWJetsToLNu.root','hist_TTWJetsToQQ.root','hist_TTZToLLNuNu.root','hist_TTZToQQ.root','hist_ttHTobb.root','hist_ttHToNonbb.root'],
        #'ST_t-channel' : ['hist_ST_t_antitop_4f.root','hist_ST_t_top_4f.root'],
        #'ST_tW' : ['hist_ST_tW_antitop_5f.root','hist_ST_tW_top_5f.root'],
        #'other' : [ 'hist_WJetsToLNu_HT1200To2500.root', 'hist_WJetsToLNu_HT200To400.root', 'hist_WJetsToLNu_HT2500ToInf.root', 'hist_WJetsToLNu_HT400To600.root', 'hist_WJetsToLNu_HT600To800.root', 'hist_WJetsToLNu_HT800To1200.root','hist_WW.root','hist_WZ.root','hist_ZZ.root','hist_TTWJetsToLNu.root','hist_TTWJetsToQQ.root','hist_TTZToLLNuNu.root','hist_TTZToQQ.root','hist_ttHTobb.root','hist_ttHToNonbb.root'],
        #'qcd': ['hist_QCD_Pt1000_MuEnriched.root', 'hist_QCD_Pt120To170_MuEnriched.root', 'hist_QCD_Pt170To300_MuEnriched.root', 'hist_QCD_Pt20To30_MuEnriched.root', 'hist_QCD_Pt300To470_MuEnriched.root', 'hist_QCD_Pt30To50_MuEnriched.root', 'hist_QCD_Pt470To600_MuEnriched.root', 'hist_QCD_Pt50To80_MuEnriched.root', 'hist_QCD_Pt600To800_MuEnriched.root', 'hist_QCD_Pt800To1000_MuEnriched.root', 'hist_QCD_Pt80To120_MuEnriched.root'],
        }

processes_mapping['data_obs'] = processes_mapping['data_all']
processes_mapping.pop('data_all')

#processes_mapping['misID'] = ['hist_fake_'+i.replace('hist_', '') for i in processes_mapping['singleTop'] + processes_mapping['other']]
#processes_mapping['misID_tt'] = ['hist_fake_'+i.replace('hist_', '') for i in processes_mapping['tt']]

smTTlist = ['tt'] # for systematics affecting only SM tt
#smTTlist = ['tt', 'misID_tt'] # for systematics affecting only SM tt
lfvlist = ['st_lfv_cs','st_lfv_ct','st_lfv_cv','st_lfv_uv','st_lfv_ut','st_lfv_us'] 

if options.applyxsec:
    # Read Xsec file
    with open(options.xsecfile, 'r') as xsec_file:
        xsec_data = yaml.load(xsec_file)
    if not xsec_data:
        print("Error loading the cross section file %s"%options.xsecfile)
        sys.exit(1)
    
def main():
    """Main function"""
    signals = ['st_lfv_cs','st_lfv_ct','st_lfv_cv','st_lfv_uv','st_lfv_ut','st_lfv_us']
    backgrounds = ['tt', 'other' , 'singleTop']
    #backgrounds = ['tt', 'other' , 'singleTop', 'misID', 'misID_tt']

    #print("Background considered: ", backgrounds)

    for signal in signals:
        for key, value in discriminants.iteritems():
            print(key, value)
        dicriminants_per_signal = dict((key,value) for key, value in discriminants.iteritems() if signal in key)
        for discriminant in dicriminants_per_signal.keys() :
            prepareShapes(backgrounds, [signal], dicriminants_per_signal[discriminant], discriminant)

def merge_histograms(process, fin, histogram, destination):
    """
    Merge two histograms together. If the destination histogram does not exist, it
    is created by cloning the input histogram

    Parameters:

    process         Name of the current process
    histogram       Pointer to TH1 to merge
    destination     Dict of destination histograms. The key is the current category.

    Return:
    The merged histogram
    """

    if not histogram:
        raise Exception('Missing histogram for %r. This should not happen.' % process)

    #if histogram.GetEntries() == 0:
    #    return

    # Rescale histogram to luminosity, if it's not data
    if not 'data' in process:
        histogram.Scale(luminosity)

    #import array
    #arr = array.array('d',[0.01, 1, 2, 5, 10, 30, 100])
    #histogram = histogram.Rebin(len(arr)-1, histogram.GetName(), arr)

    d = destination
    if not d:
        d = histogram.Clone()
        d.SetDirectory(ROOT.nullptr)
    else:
        d.Add(histogram)
    setNegativeBinsToZero(d, process)

    return d


def prepareFile(processes_map, categories_map, root_path, discriminant):
    """
    Prepare a ROOT file suitable for Combine Harvester.

    The structure is the following:
      1) Each observable is mapped to a subfolder. The name of the folder is the name of the observable
      2) Inside each folder, there's a bunch of histogram, one per background and signal hypothesis. The name of the histogram is the name of the background.
    """

    import re

    print("Preparing ROOT file for %s..."%discriminant)

    output_filename = os.path.join(options.output, 'shapes_%s.root' % (discriminant))
    if not os.path.exists(os.path.dirname(output_filename)):
        os.makedirs(os.path.dirname(output_filename))

    files = [os.path.join(root_path, f) for f in os.listdir(root_path) if f.endswith('.root')]

    # Gather a list of inputs files for each process.
    # The key is the process identifier, the value is a list of files
    # If more than one file exist for a given process, the histograms of each file will
    # be merged together later
    processes_files = {}
    for process, paths in processes_map.items():
        process_files = []
        for path in paths:
            r = re.compile(path, re.IGNORECASE)
            process_files += [f for f in files if r.search(f)]
        if len(process_files) == 0:
          print('Warning: no file found for %s'%process)
        processes_files[process] = process_files
        print("Files found for %s: "%(process), [os.path.basename(filename) for filename in process_files])

    # Create the list of histograms (nominal + systematics) for each category
    # we are interested in.
    # The key is the category name, and the value is a list of histogram. The list will always
    # contain at least one histogram (the nominal histogram), and possibly more, two per systematic (up & down variation)
    histogram_names = {}
    for discriminant_tuple in categories_map[discriminant]:
        discriminant_name = discriminant_tuple[1]
        r = re.compile(individual_discriminants[discriminant_name], re.IGNORECASE)
        #f = ROOT.TFile.Open(processes_files.values()[0][0])
        f = ROOT.TFile.Open(processes_files['tt'][0])
        histogram_names[discriminant_name] = [n.GetName() for n in f.GetListOfKeys() if r.search(n.GetName())]
        f.Close()


    # Extract list of systematics from the list of histograms derived above
    # This code assumes that *all* categories contains the same systematics (as it should)
    # The systematics list is extracted from the histogram list of the first category
    # The list of expanded histogram name is also extract (ie, regex -> full histogram name)
    systematics = set()
    histograms = {}
    systematics_regex = re.compile('__(.*)(up|down)$', re.IGNORECASE)
    #print("Histogram names :", histogram_names)
    for category, histogram_names in histogram_names.items():
        for histogram_name in histogram_names:
            #print("Histogram name :" , histogram_name)
            m = systematics_regex.search(histogram_name)
            if m:
                # It's a systematic histogram
                systematics.add(m.group(1))
            else:
                nominal_name = histogram_name
                if category in histograms:
                    # Check that the regex used by the user only match 1 histogram
                    if histograms[category] != nominal_name:
                        raise Exception("The regular expression used for category %r matches more than one histogram: %r and %r" % (category, nominal_name, histograms[category]))
                histograms[category] = nominal_name
    print("Found the following systematics in rootfiles: ", systematics)
    if options.sysToAvoid:
        for sysToAvoid in options.sysToAvoid:
            systematics.remove(sysToAvoid)

    cms_systematics = [CMSNamingConvention(s,options) for s in systematics]

    def dict_get(dict, name):
        if name in dict:
            return dict[name]
        else:
            return None

    # Create final shapes
    shapes = {}
    for category, original_histogram_name in histograms.items():
        shapes[category] = {}
        for process, process_files in processes_files.items():
            shapes[category][process] = {}

            for process_file in process_files:
                f = ROOT.TFile.Open(process_file)
                TH1 = f.Get(original_histogram_name)
                process_file_basename = os.path.basename(process_file)
                #if 'fake_' in process_file_basename: #for misID separated fit
                #    process_file_basename = process_file_basename.replace('fake_', '')
                if not TH1:
                    sys.exit()
                if options.applyxsec and not 'data' in process:
                    xsec = xsec_data[process_file_basename]['cross-section']
                    #nevt = xsec_data[process_file_basename]['generated-events']
                    histFornevt = f.Get('hcounter')
                    nevt = histFornevt.GetBinContent(2)
                    TH1.Scale(xsec/float(nevt))
                shapes[category][process]['nominal'] = merge_histograms(process, f, TH1, dict_get(shapes[category][process], 'nominal'))
                if not "data" in process: 
                    for systematic in systematics:
                        if systematic in [item for item in sysForSMtt if item not in sysForSig] \
                            and not process in smTTlist: continue
                        if systematic in sysForSMtt and not process in lfvlist + smTTlist: continue
                        for variation in ['up', 'down']:
                            key = CMSNamingConvention(systematic,options) + variation.capitalize()
                            TH1_syst = f.Get(original_histogram_name + '__' + systematic + variation)
                            if not TH1_syst:
                                # Some of misID processes are empty, just continue
                                #print("EMPTY HISTO!!!!: ", process_file, original_histogram_name + '__' + systematic + variation)
                                #continue
                                sys.exit()
                            if options.applyxsec and not 'data' in process and TH1_syst:
                                TH1_syst.Scale(xsec/float(nevt))
                            shapes[category][process][key] = merge_histograms(process, f, TH1_syst, dict_get(shapes[category][process], key))
                f.Close()

    arr = array.array('d',[0.01, 1, 2, 5, 10, 30, 100])
    #potfit muon pt
    #arr = array.array('d',[0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400])

    output_file = ROOT.TFile.Open(output_filename, 'recreate')
    for category, processes in shapes.items():
        output_file.mkdir(category).cd()
        for process, systematics_ in processes.items():
            for systematic, histogram in systematics_.items():
                histogram.SetName(process if systematic == 'nominal' else process + '__' + systematic)

                hname = histogram.GetName()

                #if ('tune' in hname) or ('hdamp' in hname) or ('jes' in hname and 'other' in hname) or ('jer' in hname and 'other' in hname):
                if ('tune' in hname) or ('hdamp' in hname) or ('jes' in hname and 'other' in hname) or ('jer' in hname and 'other' in hname) or \
                   (options.dataYear == '2016pre' and 'other' in hname):
                   #(options.dataYear == '2016pre' and 'other' in hname) or (options.dataYear == '2016post' and 'other' in hname):
                #if ('tune' in hname) or ('hdamp' in hname) or \
                #   ('jes' in hname and 'other' in hname) or \
                #   ('jer' in hname and 'other' in hname) or \
                #   ('jer' in hname and 'singleTop' in hname) or \
                #   ('fsr' in hname and 'other' in hname) or \
                #   ('muhighpt' in hname and 'other' in hname) or \
                #   ('metUnclust' in hname and 'other' in hname):

                    h_nom = shapes[category][process]['nominal']
                    h_nom.SetDirectory(ROOT.nullptr)

                    # Process up and down simultaneously
                    if 'Down' in systematic: continue
                    hist_up = histogram
                    hist_up = smoothing(hist_up, h_nom)

                    hist_dn = shapes[category][process][systematic.replace('Up', 'Down')]
                    hist_dn.SetName(process if systematic == 'nominal' else process + '__' + systematic.replace('Up', 'Down'))
                    hist_dn = smoothing(hist_dn, h_nom)

                    hist_up = hist_up.Rebin(len(arr)-1, hist_up.GetName(), arr)
                    hist_dn = hist_dn.Rebin(len(arr)-1, hist_dn.GetName(), arr)
                    h_nom = h_nom.Rebin(len(arr)-1, h_nom.GetName(), arr)

                    hist_up_to_Write = symmetrize(hist_up, hist_dn, h_nom)
                    hist_dn_to_Write = symmetrize(hist_dn, hist_up, h_nom)

                    hist_up_to_Write.Write()
                    hist_dn_to_Write.Write()

                else:
                    histogram = histogram.Rebin(len(arr)-1, histogram.GetName(), arr)
                    histogram.Write()

        output_file.cd()

    output_file.Close()
    #print("Done. File saved as %r" % output_filename)

    return output_filename, cms_systematics

def prepareShapes(backgrounds, signals, discriminant, discriminantName):
    # Backgrounds is a list of string of the considered backgrounds corresponding to entries in processes_mapping 
    # Signals is a list of string of the considered signals corresponding to entries in processes_mapping 
    # discriminant is the corresponding entry in the dictionary discriminants 

    import CombineHarvester.CombineTools.ch as ch
    root_path = options.root_path

    file, systematics = prepareFile(processes_mapping, discriminants, root_path, discriminantName)
    #call(['python', 'symmetrize.py', options.output, file, options.dataYear], shell=False)

    for signal in signals :
        cb = ch.CombineHarvester()
        cb.AddObservations(['*'], [''], ['_%s'%options.dataYear], [''], discriminant)
        cb.AddProcesses(['*'], [''], ['_%s'%options.dataYear], [''], [signal], discriminant, True)
        cb.AddProcesses(['*'], [''], ['_%s'%options.dataYear], [''], backgrounds, discriminant, False)

        # Systematics
        if not options.nosys:
            for systematic in systematics:
                if any(s_ == systematic for s_ in ['mescale', 'renscale', 'facscale', 'jesFlavorQCD']): continue
                #if any(s_ == systematic for s_ in ['jesFlavorQCD']): continue #for postfit
                systematic_only_for_SMtt = False
                systematic_only_for_Sig = False

                for systSMtt in sysForSMtt:
                    if CMSNamingConvention(systSMtt,options) == systematic:
                        systematic_only_for_SMtt = True
                for systSig in sysForSig:
                    if CMSNamingConvention(systSig,options) == systematic:
                        systematic_only_for_Sig = True
                if not systematic_only_for_SMtt and not systematic_only_for_Sig:
                    #print("No tt , no signal")
                    cb.cp().AddSyst(cb, systematic, 'shape', ch.SystMap()(1.00))
                elif systematic_only_for_SMtt and not systematic_only_for_Sig:
                    cb.cp().AddSyst(cb, systematic, 'shape', ch.SystMap('process')(smTTlist, 1.00))
                elif not systematic_only_for_SMtt and systematic_only_for_Sig:
                    cb.cp().AddSyst(cb, systematic, 'shape', ch.SystMap('process')([signal], 1.00))
                else:
                    cb.cp().AddSyst(cb, systematic, 'shape', ch.SystMap('process')(smTTlist+[signal], 1.00))

            #Lumi corr. https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM#LumiComb
            if '2016' in options.dataYear:
                cb.cp().AddSyst(cb, 'lumi_uncorr_2016', 'lnN', ch.SystMap()(1.01))
                cb.cp().AddSyst(cb, 'lumi_corr_161718', 'lnN', ch.SystMap()(1.006))
            elif options.dataYear == '2017':
                cb.cp().AddSyst(cb, 'lumi_uncorr_2017', 'lnN', ch.SystMap()(1.02))
                cb.cp().AddSyst(cb, 'lumi_corr_161718', 'lnN', ch.SystMap()(1.009))
                cb.cp().AddSyst(cb, 'lumi_corr_1718', 'lnN', ch.SystMap()(1.006))
            elif options.dataYear == '2018':
                cb.cp().AddSyst(cb, 'lumi_uncorr_2018', 'lnN', ch.SystMap()(1.015))
                cb.cp().AddSyst(cb, 'lumi_corr_161718', 'lnN', ch.SystMap()(1.02))
                cb.cp().AddSyst(cb, 'lumi_corr_1718', 'lnN', ch.SystMap()(1.002))

            cb.cp().AddSyst(cb, 'xsec_tt', 'lnN', ch.SystMap('process')(['tt'], 1.044))
            cb.cp().AddSyst(cb, 'xsec_ttX', 'lnN', ch.SystMap('process')(['TTX'], 1.2))
            cb.cp().AddSyst(cb, 'xsec_vv', 'lnN', ch.SystMap('process')(['vv'], 1.1))
            cb.cp().AddSyst(cb, 'xsec_dy', 'lnN', ch.SystMap('process')(['DY'], 1.1))
            cb.cp().AddSyst(cb, 'xsec_wjets', 'lnN', ch.SystMap('process')(['wJets'], 1.1))
            cb.cp().AddSyst(cb, 'xsec_singleTop', 'lnN', ch.SystMap('process')(['singleTop'], 1.1))
            cb.cp().AddSyst(cb, 'xsec_Other', 'lnN', ch.SystMap('process')(['other'], 1.1))
            #cb.cp().AddSyst(cb, 'rate_misID', 'rateParam', ch.SystMap('process')(['misID'], 1.0))
            #cb.cp().AddSyst(cb, 'rate_misID_tt', 'rateParam', ch.SystMap('process')(['misID_tt'], 1.0))
            #cb.cp().AddSyst(cb, 'rate_misID', 'lnN', ch.SystMap('process')(['misID'], 2.0))
            #cb.cp().AddSyst(cb, 'rate_misID_tt', 'lnN', ch.SystMap('process')(['misID_tt'], 1.5))

        # Import shapes from ROOT file
        cb.cp().backgrounds().ExtractShapes(file, '$BIN/$PROCESS', '$BIN/$PROCESS__$SYSTEMATIC')
        cb.cp().signals().ExtractShapes(file, '$BIN/$PROCESS', '$BIN/$PROCESS__$SYSTEMATIC')

        #rebin = ch.AutoRebin().SetBinThreshold(50).SetBinUncertFraction(0.10).SetVerbosity(1)
        #rebin.Rebin(cb.cp(), cb)

        #AutoMCStat
        cb.SetAutoMCStats(cb, 0.1)

        output_prefix = 'TOP_LFV_%s_Discriminant_%s' % (signal, discriminantName)

        output_dir = os.path.join(options.output, '%s' % (signal))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        fake_mass = '125'

        # Write card
        datacard = os.path.join(output_dir, output_prefix + '.dat')
        cb.cp().mass([fake_mass, "*"]).WriteDatacard(os.path.join(output_dir, output_prefix + '.dat'), os.path.join(output_dir, output_prefix + '_shapes.root'))

        # Write small script to compute the limit
        workspace_file = os.path.basename(os.path.join(output_dir, output_prefix + '_combine_workspace.root'))
        script = """#! /bin/bash

text2workspace.py {datacard} -m {fake_mass} -o {workspace_root}

# Run limit

echo combine -M AsymptoticLimits -n {name} {workspace_root} #--run blind #-v +2
#combine -M AsymptoticLimits -n {name} {workspace_root} --run blind --rMin -1 --rMax 1 --rAbsAcc 0.0000005 --cminDefaultMinimizerStrategy 0 #-v +2
combine -M AsymptoticLimits -n {name} {workspace_root} --rMin -1 --rMax 1 --rAbsAcc 0.0000005 --cminDefaultMinimizerStrategy 0 #-v +2
#combine -M AsymptoticLimits -n {name} {workspace_root} --rMin -1 --rMax 1 --rAbsAcc 0.0000005 --cminDefaultMinimizerStrategy 0 --setParameters rate_misID=1.,rate_misID_tt=1. --setParameterRanges rate_misID=0.,2.:rate_misID_tt=0.,2. #-v +2
#combine -H AsymptoticLimits -M HybridNew -n {name} {workspace_root} --LHCmode LHC-limits --expectedFromGrid 0.5 #for ecpected, use 0.84 and 0.16

combine -M MultiDimFit {name}_combine_workspace.root -n .NLLScan --rMin -0.5 --rMax 0.5 --algo grid --points 200
python ../../plot1DScan.py higgsCombine.NLLScan.MultiDimFit.mH120.root -o single_scan_{year}_{signal}
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, fake_mass=fake_mass, year=options.dataYear, signal=signal, systematics=(0 if options.nosys else 1))
        script_file = os.path.join(output_dir, output_prefix + '_run_limits.sh')
        with open(script_file, 'w') as f:
            f.write(script)
        
        st = os.stat(script_file)
        os.chmod(script_file, st.st_mode | stat.S_IEXEC)


        # Write small script for impacts
        script = """#! /bin/bash

# Run impacts
combineTool.py -M FastScan -w {name}_combine_workspace.root:w -o {name}_{year}_nll

combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --doInitialFit --rMin -20 --rMax 20 -t -1
combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --doFits --rMin -20 --rMax 20 -t -1 --parallel 50
combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 -o {name}_{year}_expected_impacts.json --rMin -20 --rMax 20 -t -1
plotImpacts.py -i {name}_{year}_expected_impacts.json -o {name}_{year}_expected_impacts --per-page 50

combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --doInitialFit --rMin -20 --rMax 20
combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --doFits --rMin -20 --rMax 20 --parallel 50
combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 -o {name}_{year}_impacts.json --rMin -20 --rMax 20
plotImpacts.py -i {name}_{year}_impacts.json -o {name}_{year}_impacts --per-page 50

#combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --doInitialFit --rMin -20 --rMax 20 -t -1 --setParameters rate_misID=1.,rate_misID_tt=1. --setParameterRanges rate_misID=0.,2.:rate_misID_tt=0.,2.
#combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --doFits --rMin -20 --rMax 20 -t -1 --parallel 50 --setParameters rate_misID=1.,rate_misID_tt=1. --setParameterRanges rate_misID=0.,2.:rate_misID_tt=0.,2.
#combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 -o {name}_{year}_expected_impacts.json --rMin -20 --rMax 20 -t -1
#plotImpacts.py -i {name}_{year}_expected_impacts.json -o {name}_{year}_expected_impacts --per-page 50
#
#combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --doInitialFit --rMin -20 --rMax 20 --setParameters rate_misID=1.,rate_misID_tt=1. --setParameterRanges rate_misID=0.,2.:rate_misID_tt=0.,2.
#combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --doFits --rMin -20 --rMax 20 --parallel 50 --setParameters rate_misID=1.,rate_misID_tt=1. --setParameterRanges rate_misID=0.,2.:rate_misID_tt=0.,2.
#combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 -o {name}_{year}_impacts.json --rMin -20 --rMax 20
#plotImpacts.py -i {name}_{year}_impacts.json -o {name}_{year}_impacts --per-page 50
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, year=options.dataYear, fake_mass=fake_mass, systematics=(0 if options.nosys else 1))
        script_file = os.path.join(output_dir, output_prefix + '_run_impacts.sh')
        with open(script_file, 'w') as f:
            f.write(script)
        
        st = os.stat(script_file)
        os.chmod(script_file, st.st_mode | stat.S_IEXEC)

        # Write small script for postfit shapes
        script = """#! /bin/bash

# Run postfit
echo combine -M FitDiagnostics {datacard} -n _{name}_postfit --saveNormalizations --saveShapes --saveWithUncertainties --preFitValue 0 --rMin -20 --rMax 20 -v 1
combine -M FitDiagnostics {datacard} -n _{name}_postfit --saveNormalizations --saveShapes --saveWithUncertainties --preFitValue 0 --rMin -20 --rMax 20 -v 1 #--plots
PostFitShapesFromWorkspace -w {name}_combine_workspace.root -d {datacard} -o postfit_shapes_{name}.root -f fitDiagnostics_{name}_postfit.root:fit_b --postfit --sampling
python ../../convertPostfitShapesForPlotIt.py -i postfit_shapes_{name}.root
../../plotIt/plotIt -o postfit_shapes_TOP_LFV_forPlotIt ../../plotIt/configs/TOP-22-011/postfit_config_{year}.yml -y --allSig --selectSig {signal}
cd postfit_shapes_TOP_LFV_forPlotIt
mv DNN_logx_logy.pdf DNN_{signal}_{year}_logx_logy.pdf
mv DNN_logx_logy.png DNN_{signal}_{year}_logx_logy.png
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, fake_mass=fake_mass, systematics=(0 if options.nosys else 1), year=options.dataYear, signal=signal)
        script_file = os.path.join(output_dir, output_prefix + '_run_postfit.sh')
        with open(script_file, 'w') as f:
            f.write(script)
        
        st = os.stat(script_file)
        os.chmod(script_file, st.st_mode | stat.S_IEXEC)

def CMSNamingConvention(syst, options):
    syst_year = 'Y' + options.dataYear
    if '2016' in options.dataYear: syst_year = "Y2016"
    if syst not in correlatedSys:
        return syst_year + '_' + syst
    elif options.dataYear in syst:
        return syst_year + '_' + syst
    else:
        return syst

if __name__ == '__main__':
    main()

