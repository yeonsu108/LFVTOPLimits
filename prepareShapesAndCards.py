#! /bin/env python

# Python imports
import os, sys, stat, argparse, getpass, json
from datetime import datetime
from math import sqrt
import yaml

# to prevent pyroot to hijack argparse we need to go around
tmpargv = sys.argv[:] 
sys.argv = []

# ROOT imports
import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True
sys.argv = tmpargv

hadNegBinForProcess = {}
def setNegativeBinsToZero(h, process):
    if not process in hadNegBinForProcess:
        hadNegBinForProcess[process] = False
    for i in range(1, h.GetNbinsX() + 1):
        if h.GetBinContent(i) < 0.:
            if not hadNegBinForProcess[process]:
                print 'Remove negative bin in TH1 %s for process %s'%(h.GetTitle(), process)
            hadNegBinForProcess[process] = True
            h.SetBinContent(i, 0.)
    
def get_hist_regex(r):
    return '^%s(__.*(up|down))?$' % r


parser = argparse.ArgumentParser(description='Create shape datacards ready for combine')

parser.add_argument('-p', '--path', action='store', dest='root_path', type=str, default='/afs/cern.ch/user/b/brfranco/work/public/FCNC/limits/rootfiles_for_limits/histos_suitable_for_limits_190121_TTsigSplit/', help='Directory containing rootfiles with the TH1 used for limit settings')
#parser.add_argument('-p', '--path', action='store', dest='root_path', type=str, default='/afs/cern.ch/user/b/brfranco/work/public/FCNC/limits/rootfiles_for_limits/DNN_181109_j3b2/', help='Directory containing rootfiles with the TH1 used for limit settings')
parser.add_argument('-l', '--luminosity', action='store', type=float, dest='luminosity', default=41529, help='Integrated luminosity (default is 41529 /pb)')
parser.add_argument('-o', '--output', action='store', dest='output', type=str, default='datacards_rebinned_190121_play', help='Output directory')
parser.add_argument('-c' , '--channel', action='store', dest='channel', type=str, default='all', help='Channel: el, mu, or all.')
parser.add_argument('-applyxsec' , action='store', dest='applyxsec', type=bool, default=True, help='Reweight MC processes by Xsec/Nevt from yml config.')
parser.add_argument('-xsecfile' , action='store', dest='xsecfile', type=str, default='xsec_sig1pb.yml', help='YAML config file path with Xsec and Nevt.')
parser.add_argument('--reweight', action='store_true', dest='reweight', help='Apply a preliminary reweighting. Not implemented yet.')
parser.add_argument('--fake-data', action='store_true', dest='fake_data', help='Use fake data instead of real data')
parser.add_argument('--SF', action='store_true', dest='SF', help='Produce cards for scale factors extraction (add line with rateParam). Not final yet!')
parser.add_argument('--nosys', action='store', dest='nosys', default=False, help='Consider or not systematic uncertainties (NB : bbb uncertainty is with another flag)')
parser.add_argument('--sysToAvoid', action='store', dest='sysToAvoid', nargs='+', help='Set it to exclude some of the systematics')
# Example to call it: python prepareShapesAndCards.py --sysToAvoid pu hf
parser.add_argument('--sysForSMtt', action='store', dest='sysForSMtt', nargs='+', default=['scale', 'TuneCP5', 'ps', 'pdf'], help='Systematics affecting only SM tt.')
parser.add_argument('--nobbb', action='store_true', help='Consider or not bin by bin MC stat systematic uncertainties')
parser.add_argument('--test', action='store_true', help='Do not prepare all categories, fasten the process for development')
parser.add_argument('-rebinning' , action='store', dest='rebinning', type=int, default=4, help='Rebin the histograms by -rebinning.')

options = parser.parse_args()

channel_mapping = {
    "mu" : 'Ch0',
    "el" : 'Ch1',
    "all" : 'Ch2'
    }

selection_mapping = {
    'b2j3' : 'S2',
    'b2j4' : 'S6',
    'b3j3' : 'S3',
    'b3j4' : 'S7',
    'b4j4' : 'S11'
    }

#Hct_j4_h_DNN_b2_Ch2__TuneCP5up
DNN_Hct_hist_name = 'Hct'
DNN_Hut_hist_name = 'Hut'
channel = options.channel 
individual_discriminants = { # support regex (allow to avoid ambiguities if many histogram contains same patterns)
        #'DNN_Hct_b2j3': get_hist_regex('{0}_j3_h_DNN_b2_{1}'.format(DNN_Hct_hist_name, channel_mapping[channel])),
        #'DNN_Hct_b3j3': get_hist_regex('{0}_j3_h_DNN_b3_{1}'.format(DNN_Hct_hist_name, channel_mapping[channel])),

        #'DNN_Hct_b2j4': get_hist_regex('{0}_j4_h_DNN_b2_{1}'.format(DNN_Hct_hist_name, channel_mapping[channel])),
        #'DNN_Hct_b3j4': get_hist_regex('{0}_j4_h_DNN_b3_{1}'.format(DNN_Hct_hist_name, channel_mapping[channel])),
        #'DNN_Hct_b4j4': get_hist_regex('{0}_j4_h_DNN_b4_{1}'.format(DNN_Hct_hist_name, channel_mapping[channel])),

        #'DNN_Hut_b2j3': get_hist_regex('{0}_j3_h_DNN_b2_{1}'.format(DNN_Hut_hist_name, channel_mapping[channel])),
        #'DNN_Hut_b3j3': get_hist_regex('{0}_j3_h_DNN_b3_{1}'.format(DNN_Hut_hist_name, channel_mapping[channel])),

        #'DNN_Hut_b2j4': get_hist_regex('{0}_j4_h_DNN_b2_{1}'.format(DNN_Hut_hist_name, channel_mapping[channel])),
        #'DNN_Hut_b3j4': get_hist_regex('{0}_j4_h_DNN_b3_{1}'.format(DNN_Hut_hist_name, channel_mapping[channel])),
        #'DNN_Hut_b4j4': get_hist_regex('{0}_j4_h_DNN_b4_{1}'.format(DNN_Hut_hist_name, channel_mapping[channel])),
        ##########################################################################################################
        'DNN_Hct_b2j3': get_hist_regex('{0}_j3b2_h_DNN_b2_{1}'.format(DNN_Hct_hist_name, channel_mapping[channel])),
        'DNN_Hct_b3j3': get_hist_regex('{0}_j3b3_h_DNN_b3_{1}'.format(DNN_Hct_hist_name, channel_mapping[channel])),

        'DNN_Hct_b2j4': get_hist_regex('{0}_j4b2_h_DNN_b2_{1}'.format(DNN_Hct_hist_name, channel_mapping[channel])),
        'DNN_Hct_b3j4': get_hist_regex('{0}_j4b3_h_DNN_b3_{1}'.format(DNN_Hct_hist_name, channel_mapping[channel])),
        'DNN_Hct_b4j4': get_hist_regex('{0}_j4b4_h_DNN_b4_{1}'.format(DNN_Hct_hist_name, channel_mapping[channel])),

        'DNN_Hut_b2j3': get_hist_regex('{0}_j3b2_h_DNN_b2_{1}'.format(DNN_Hut_hist_name, channel_mapping[channel])),
        'DNN_Hut_b3j3': get_hist_regex('{0}_j3b3_h_DNN_b3_{1}'.format(DNN_Hut_hist_name, channel_mapping[channel])),

        'DNN_Hut_b2j4': get_hist_regex('{0}_j4b2_h_DNN_b2_{1}'.format(DNN_Hut_hist_name, channel_mapping[channel])),
        'DNN_Hut_b3j4': get_hist_regex('{0}_j4b3_h_DNN_b3_{1}'.format(DNN_Hut_hist_name, channel_mapping[channel])),
        'DNN_Hut_b4j4': get_hist_regex('{0}_j4b4_h_DNN_b4_{1}'.format(DNN_Hut_hist_name, channel_mapping[channel])),
        ##########################################################################################################

        #'BDT_Hct_b2j3': get_hist_regex('{0}_j3b2_h_DNN_b2_{1}'.format(DNN_Hct_hist_name, channel_mapping[channel])),
        #'DNN_Hct_b2j3': get_hist_regex('{0}_j3b2_h_DNN_b2_{1}'.format(DNN_Hct_hist_name, channel_mapping[channel])),

        #'DNN_Hct_b2j3': get_hist_regex('{0}_j3_h_DNN_b2_{2}'.format(DNN_Hct_hist_name, channel_mapping[channel])),
        #'DNN_Hct_b2j4': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hct_hist_name, channel_mapping[channel], selection_mapping['b2j4'])),
        #'DNN_Hct_b3j3': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hct_hist_name, channel_mapping[channel], selection_mapping['b3j3'])),
        #'DNN_Hct_b3j4': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hct_hist_name, channel_mapping[channel], selection_mapping['b3j4'])),
        #'DNN_Hct_b4j4': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hct_hist_name, channel_mapping[channel], selection_mapping['b4j4'])),
        #'DNN_Hut_b2j3': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hut_hist_name, channel_mapping[channel], selection_mapping['b2j3'])),
        #'DNN_Hut_b2j4': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hut_hist_name, channel_mapping[channel], selection_mapping['b2j4'])),
        #'DNN_Hut_b3j3': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hut_hist_name, channel_mapping[channel], selection_mapping['b3j3'])),
        #'DNN_Hut_b3j4': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hut_hist_name, channel_mapping[channel], selection_mapping['b3j4'])),
        #'DNN_Hut_b4j4': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hut_hist_name, channel_mapping[channel], selection_mapping['b4j4'])),
        #'yields': get_hist_regex('yields(?!(_sf|_df))'),
        }
        
discriminants = { # 'name of datacard' : list of tuple with (dicriminant ID, name in 'individual_discriminants' dictionary above). Make sure the 'name of datacard' ends with '_categoryName (for plot step)
    "DNN_Hct_b2j3" : [(1, 'DNN_Hct_b2j3')],
    "DNN_Hct_b2j4" : [(1, 'DNN_Hct_b2j4')],
    "DNN_Hct_b3j3" : [(1, 'DNN_Hct_b3j3')],
    "DNN_Hct_b3j4" : [(1, 'DNN_Hct_b3j4')],
    "DNN_Hct_b4j4" : [(1, 'DNN_Hct_b4j4')],
    "DNN_Hct_all" : [(1, 'DNN_Hct_b2j3'), (2, 'DNN_Hct_b2j4'), (3, 'DNN_Hct_b3j3'), (4, 'DNN_Hct_b3j4'), (5, 'DNN_Hct_b4j4')],
    "DNN_Hut_b2j3" : [(1, 'DNN_Hut_b2j3')],
    "DNN_Hut_b2j4" : [(1, 'DNN_Hut_b2j4')],
    "DNN_Hut_b3j3" : [(1, 'DNN_Hut_b3j3')],
    "DNN_Hut_b3j4" : [(1, 'DNN_Hut_b3j4')],
    "DNN_Hut_b4j4" : [(1, 'DNN_Hut_b4j4')],
    "DNN_Hut_all" : [(1, 'DNN_Hut_b2j3'), (2, 'DNN_Hut_b2j4'), (3, 'DNN_Hut_b3j3'), (4, 'DNN_Hut_b3j4'), (5, 'DNN_Hut_b4j4')],

    # tests
    #"BDT_Hct_b2j3" : [(1, 'BDT_Hct_b2j3')],
    }
if options.test:
    discriminants = { "DNN_Hut_all" : [(1, 'DNN_Hut_b2j3'), (2, 'DNN_Hut_b2j4'), (3, 'DNN_Hut_b3j3'), (4, 'DNN_Hut_b3j4'), (5, 'DNN_Hut_b4j4')],
            #"DNN_Hct_b3j3" : [(1, 'DNN_Hct_b3j3')] 
            }
# Our definition of Bkg
#processes_mapping = { # Dict with { key(human friendly name of your choice) : value(regex to find rootfile) }. Be carefull not to match too many files with the regex!
#                      # Data !Must! contain 'data_%channels' in the key and MC must not have data in the key
#        # Background
#        ## TT Semileptonic 
#        'ttother': ['hist_TTpowhegttother.root'],
#        'ttlf': ['hist_TTpowhegttlf.root'],
#        'ttcc': ['hist_TTpowhegttcc.root'],
#        'ttbj' : ['hist_TTpowhegttbj.root'],
#        'ttbb': ['TTpowhegttbb'],
#        ## Other Top
#        'tthad': ['hist_TTHadpowheg.root'],
#        'ttfullLep': ['hist_TTLLpowheg.root'],
#        'SingleTop': ['.*SingleT.*'],
#        'ttV': ['hist_TTWJetsToLNuPSweight.root', 'hist_TTWJetsToQQ.root', 'hist_TTZToLLNuNu.root', 'hist_TTZToQQ.root'],
#        ## V + jets
#        'Wjets': ['hist_W1JetsToLNu.root', 'hist_W2JetsToLNu.root', 'hist_W3JetsToLNu.root', 'hist_W4JetsToLNu.root'],
#        'DYjets': ['hist_DYJets.*'],
#        ## VV
#        'VV': ['hist_WW.root', 'hist_WZ.root', 'hist_ZZ.root'],
#        ## Higgs
#        'tth': ['hist_ttHTobb.root', 'hist_ttHToNonbb.root'],
#        # Signal
#        'Hut': ['TTTH1L3BHut', 'STTH1L3BHut'],
#        'Hct': ['TTTH1L3BHct', 'STTH1L3BHct'],
#        #'Hct': ['STTH1L3BHct'],
#        # Data
#        'data_el' : ['SingleElectronRun2017'],
#        'data_mu' : ['SingleMuonRun2017'],
#        'data_all' : ['Single.*Run2017']
#        }
#processes_mapping['data_obs'] = processes_mapping['data_%s'%channel]
#processes_mapping.pop('data_el')
#processes_mapping.pop('data_mu')
#processes_mapping.pop('data_all')
#
#smTTlist = ['ttother', 'ttlf', 'ttcc', 'ttbj', 'ttbb', 'tthad', 'ttfullLep'] # for systematics affecting only SM tt

# IF you change Bkg Def, don't forget to change also the backgrounds list in main and the systematics for cross sections

# ~Kirill definition of Bkg
processes_mapping = { # Dict with { key(human friendly name of your choice) : value(regex to find rootfile) }. Be carefull not to match too many files with the regex!
                      # Data !Must! contain 'data_%channels' in the key and MC must not have data in the key
        # Background
        ## TT Semileptonic 
        'ttlf': ['hist_TTpowhegttlf.root'],
        'ttcc': ['hist_TTpowhegttcc.root'],
        'ttbj' : ['hist_TTpowhegttbj.root'],
        'ttbb': ['TTpowhegttbb'],
        ## Other Top
        'ttother': ['hist_TTpowhegttother.root', 'hist_TTHadpowheg.root', 'hist_TTLLpowheg.root'],
        ## Other Bkg
        'SingleTop': ['.*SingleT.*'],
        'other' : ['hist_TTWJetsToLNuPSweight.root', 'hist_TTWJetsToQQ.root', 'hist_TTZToLLNuNu.root', 'hist_TTZToQQ.root', 'hist_W1JetsToLNu.root', 'hist_W2JetsToLNu.root', 'hist_W3JetsToLNu.root', 'hist_W4JetsToLNu.root', 'hist_DYJets.*', 'hist_WW.root', 'hist_WZ.root', 'hist_ZZ.root', 'hist_ttHTobb.root', 'hist_ttHToNonbb.root'],
#        'tthad': ['hist_TTHadpowheg.root'],
#        'ttfullLep': ['hist_TTLLpowheg.root'],
#        'SingleTop': ['.*SingleT.*'],
#        'ttV': ['hist_TTWJetsToLNuPSweight.root', 'hist_TTWJetsToQQ.root', 'hist_TTZToLLNuNu.root', 'hist_TTZToQQ.root'],
#        ## V + jets
#        'Wjets': ['hist_W1JetsToLNu.root', 'hist_W2JetsToLNu.root', 'hist_W3JetsToLNu.root', 'hist_W4JetsToLNu.root'],
#        'DYjets': ['hist_DYJetsv2.*'],
#        ## VV
#        'VV': ['hist_WW.root', 'hist_WZ.root', 'hist_ZZ.root'],
#        ## Higgs
#        'tth': ['hist_ttHTobb.root', 'hist_ttHToNonbb.root'],
        # Signal
        #'Hut': ['TTTH1L3BHut', 'STTH1L3BHut'],
        #'Hct': ['TTTH1L3BHct', 'STTH1L3BHct'],
        'Hut': ['TTTH1L3BaTLepHut', 'TTTH1L3BTLepHut', 'STTH1L3BHut'],
        'Hct': ['TTTH1L3BaTLepHct', 'TTTH1L3BTLepHct', 'STTH1L3BHct'],
        #'Hct': ['STTH1L3BHct'],
        # Data
        'data_el' : ['SingleElectronRun2017'],
        'data_mu' : ['SingleMuonRun2017'],
        'data_all' : ['Single.*Run2017']
        }
processes_mapping['data_obs'] = processes_mapping['data_%s'%channel]
processes_mapping.pop('data_el')
processes_mapping.pop('data_mu')
processes_mapping.pop('data_all')

smTTlist = ['ttlf', 'ttcc', 'ttbj', 'ttbb', 'ttother'] # for systematics affecting only SM tt

if options.fake_data:
  print "Fake data mode not implemented yet! Exitting..."
  sys.exit(1)

if options.applyxsec:
    # Read Xsec file
    with open(options.xsecfile, 'r') as xsec_file:
        xsec_data = yaml.load(xsec_file)
    if not xsec_data:
        print "Error loading the cross section file %s"%options.xsecfile
        sys.exit(1)
    
def main():
    """Main function"""
    signals = ['Hut', 'Hct']
    #backgrounds = ['ttother', 'ttlf', 'ttcc', 'ttbj', 'ttbb', 'tthad', 'ttfullLep', 'SingleTop', 'ttV', 'Wjets', 'DYjets', 'VV', 'tth']
    backgrounds = ['ttlf', 'ttcc', 'ttbj', 'ttbb', 'ttother', 'other', 'SingleTop']
    print "Background considered: ", backgrounds

    for signal in signals:
        dicriminants_per_signal = dict((key,value) for key, value in discriminants.iteritems() if signal in key)
        for discriminant in dicriminants_per_signal.keys() :
            prepareShapes(backgrounds, [signal], dicriminants_per_signal[discriminant], discriminant)

def merge_histograms(process, histogram, destination):
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
        #print "Rescaleing %s to lumi: "%process, options.luminosity
        histogram.Scale(options.luminosity)
    #print process, " ", histogram.GetTitle(), " ", destination, " ", histogram.GetNbinsX()
    histogram.Rebin(options.rebinning)

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
          print 'Warning: no file found for %s'%process
        processes_files[process] = process_files
        print "Files found for %s: "%(process), [os.path.basename(filename) for filename in process_files]

    # Create the list of histograms (nominal + systematics) for each category
    # we are interested in.
    # The key is the category name, and the value is a list of histogram. The list will always
    # contain at least one histogram (the nominal histogram), and possibly more, two per systematic (up & down variation)
    histogram_names = {}
    for discriminant_tuple in categories_map[discriminant]:
        discriminant_name = discriminant_tuple[1]
        r = re.compile(individual_discriminants[discriminant_name], re.IGNORECASE)
        f = ROOT.TFile.Open(processes_files.values()[0][0])
        histogram_names[discriminant_name] = [n.GetName() for n in f.GetListOfKeys() if r.search(n.GetName())]
        f.Close()

    #for category, histogram_name in categories_map.items():
    #    r = re.compile(histogram_name, re.IGNORECASE)
    #    f = ROOT.TFile.Open(processes_files.values()[0][0])
    #    histogram_names[category] = [n.GetName() for n in f.GetListOfKeys() if r.search(n.GetName())]
    #    f.Close()

    # Extract list of systematics from the list of histograms derived above
    # This code assumes that *all* categories contains the same systematics (as it should)
    # The systematics list is extracted from the histogram list of the first category
    # The list of expanded histogram name is also extract (ie, regex -> full histogram name)
    systematics = set()
    histograms = {}
    systematics_regex = re.compile('__(.*)(up|down)$', re.IGNORECASE)
    for category, histogram_names in histogram_names.items():
        for histogram_name in histogram_names:
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
    print "Found the following systematics in rootfiles: ", systematics
    if options.sysToAvoid:
        for sysToAvoid in options.sysToAvoid:
            systematics.discard(sysToAvoid)
        print "After ignoring the one mentioned with sysToAvoid option: ", systematics

    print systematics
    cms_systematics = [CMSNamingConvention(s) for s in systematics]

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
                if not TH1:
                    print "No histo named %s in %s. Exitting..."%(original_histogram_name, process_file)
                    sys.exit()
                if options.applyxsec and not 'data' in process:
                    xsec = xsec_data[process_file_basename]['cross-section']
                    nevt = xsec_data[process_file_basename]['generated-events']
                    #print "Applying cross sec and nevt on %s "%process_file_basename, xsec, " ", nevt, " --> ", xsec/float(nevt)
                    TH1.Scale(xsec/float(nevt))
                if options.reweight :
                    print 'Reweighting on the flight not implemented yet! Exitting...'
                    # if you implement it, don't forget also to scale TH1 for systematics
                    sys.exit(1)
                    if "DY" in process_file :
                        if not ('DYJetsToLL_M-10to50') in process_file:
                            print "Reweight ", process_file, " by 0.75950" 
                            TH1.Scale(0.75950)
                shapes[category][process]['nominal'] = merge_histograms(process, TH1, dict_get(shapes[category][process], 'nominal'))
                if not "data" in process: 
                    for systematic in systematics:
                        if systematic in options.sysForSMtt and not process in smTTlist:
                            continue
                        for variation in ['up', 'down']:
                            key = CMSNamingConvention(systematic) + variation.capitalize()
                            #print "Key: ", key
                            TH1_syst = f.Get(original_histogram_name + '__' + systematic + variation)
                            #if systematic in options.sysForSMtt and not process in smTTlist:
                            #    # Copy nominal TH1 in non SMtt processes for systematics affecting only SMtt (already scaled)
                            #    shapes[category][process][key] = merge_histograms(process, TH1, dict_get(shapes[category][process], key))
                            #    continue
                            if not TH1_syst:
                                print "No histo named %s in %s"%(original_histogram_name + '__' + systematic + variation, process_file_basename)
                                sys.exit()
                            if options.applyxsec and not 'data' in process:
                                #process_file_basename = os.path.basename(process_file)
                                #xsec = xsec_data[process_file_basename]['cross-section']
                                #nevt = xsec_data[process_file_basename]['generated-events']
                                TH1_syst.Scale(xsec/float(nevt))
                            shapes[category][process][key] = merge_histograms(process, TH1_syst, dict_get(shapes[category][process], key))
                f.Close()

    output_file = ROOT.TFile.Open(output_filename, 'recreate')

    if options.fake_data:
        print "Fake data mode not implemented yet! Exitting..."
        sys.exit(1)
        for category, processes in shapes.items():
            fake_data = None
            for process, systematics_dict in processes.items():
                if not fake_data:
                    fake_data = systematics_dict['nominal'].Clone()
                    fake_data.SetDirectory(ROOT.nullptr)
                else:
                    fake_data.Add(systematics_dict['nominal'])
            processes['data_obs'] = {'nominal': fake_data}

    for category, processes in shapes.items():
        output_file.mkdir(category).cd()
        for process, systematics_ in processes.items():
            for systematic, histogram in systematics_.items():
                histogram.SetName(process if systematic == 'nominal' else process + '__' + systematic)
                histogram.Write()
        output_file.cd()

    output_file.Close()
    print("Done. File saved as %r" % output_filename)

    return output_filename, cms_systematics

def prepareShapes(backgrounds, signals, discriminant, discriminantName):
    # Backgrounds is a list of string of the considered backgrounds corresponding to entries in processes_mapping 
    # Signals is a list of string of the considered signals corresponding to entries in processes_mapping 
    # discriminant is the corresponding entry in the dictionary discriminants 

    import CombineHarvester.CombineTools.ch as ch
    root_path = options.root_path

    file, systematics = prepareFile(processes_mapping, discriminants, root_path, discriminantName)
    
    for signal in signals :
        cb = ch.CombineHarvester()
        cb.AddObservations(['*'], [''], ['13TeV_2017'], [''], discriminant)
        cb.AddProcesses(['*'], [''], ['13TeV_2017'], [''], backgrounds, discriminant, False)
        cb.AddProcesses(['*'], [''], ['13TeV_2017'], [''], [signal], discriminant, True)

        # Systematics
        if not options.nosys:
            for systematic in systematics:
                if not systematic in options.sysForSMtt:
                    cb.cp().AddSyst(cb, systematic, 'shape', ch.SystMap()(1.00))
                else:
                    #cb.cp().AddSyst(cb, '$PROCESS_'+systematic, 'shape', ch.SystMap('process')(['ttother', 'ttlf', 'ttbj', 'tthad', 'ttfullLep'], 1.00))
                    cb.cp().AddSyst(cb, systematic, 'shape', ch.SystMap('process')(smTTlist, 1.00))
            cb.cp().AddSyst(cb, 'lumi_$ERA', 'lnN', ch.SystMap('era')(['13TeV_2017'], 1.023))
            cb.cp().AddSyst(cb, 'tt_xsec', 'lnN', ch.SystMap('process')
                    (['ttbb', 'ttcc', 'ttother', 'ttlf', 'ttbj'], 1.055)
                    )
            cb.cp().AddSyst(cb, '$PROCESS_norm', 'lnN', ch.SystMap('process')
                    (['ttbb'], 1.3)
                    )
            cb.cp().AddSyst(cb, '$PROCESS_norm', 'lnN', ch.SystMap('process')
                    (['ttcc'], 1.5)
                    )
            cb.cp().AddSyst(cb, 'Other_xsec', 'lnN', ch.SystMap('process')
                    #(['SingleTop', 'ttV', 'Wjets', 'DYjets', 'VV', 'tth'], 1.1)
                    (['SingleTop', 'other'], 1.1)
                    )
        if options.SF :
            print "Background renormalization is deprecated! Exitting..."
            sys.exit(1)
            cb.cp().AddSyst(cb, 'SF_$PROCESS', 'rateParam', ch.SystMap('process')
                    (['ttbb'], 1.)
                    )

        # Import shapes from ROOT file
        cb.cp().backgrounds().ExtractShapes(file, '$BIN/$PROCESS', '$BIN/$PROCESS__$SYSTEMATIC')
        cb.cp().signals().ExtractShapes(file, '$BIN/$PROCESS', '$BIN/$PROCESS__$SYSTEMATIC')

        # Bin by bin uncertainties
        if not options.nobbb:
            print "Treating bbb"
            bbb = ch.BinByBinFactory()
            #bbb.SetAddThreshold(0.1).SetMergeThreshold(0.5).SetFixNorm(True)
            bbb.SetAddThreshold(0.1)
            bbb.AddBinByBin(cb.cp().backgrounds(), cb)
            bbb.AddBinByBin(cb.cp().signals(), cb)

        if options.nosys and options.nobbb : 
            cb.cp().AddSyst(cb, 'lumi_$ERA', 'lnN', ch.SystMap('era')(['13TeV_2017'], 1.00001)) # Add a negligible systematic (chosen to be lumi) to trick combine

        output_prefix = 'FCNC_%s_Discriminant_%s' % (signal, discriminantName)

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

echo combine -M AsymptoticLimits -n {name} {workspace_root} -S {systematics} --run expected #-v +2
combine -M AsymptoticLimits -n {name} {workspace_root} -S {systematics} --run expected #-v +2
#combine -H AsymptoticLimits -M HybridNew -n {name} {workspace_root} -S {systematics} --LHCmode LHC-limits --expectedFromGrid 0.5 #for ecpected, use 0.84 and 0.16
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, fake_mass=fake_mass, systematics=(0 if options.nosys else 1))
        script_file = os.path.join(output_dir, output_prefix + '_run_limits.sh')
        with open(script_file, 'w') as f:
            f.write(script)
        
        st = os.stat(script_file)
        os.chmod(script_file, st.st_mode | stat.S_IEXEC)


        # Write small script for datacard checks
        script = """#! /bin/bash

# Run checks
echo combine -M MaxLikelihoodFit -t -1 --expectSignal 0 {datacard} -n fitDiagnostics_{name}_bkgOnly
echo python ../../../../HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a fitDiagnostics_{name}_bkgOnly.root -g fitDiagnostics_{name}_bkgOnly_plots.root
combine -M MaxLikelihoodFit -t -1 --expectSignal 0 {datacard} -n _{name}_bkgOnly 
python ../../../../HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a fitDiagnostics_{name}_bkgOnly.root -g fitDiagnostics_{name}_bkgOnly_plots.root
python ../../printPulls.py fitDiagnostics_{name}_bkgOnly_plots.root
combine -M MaxLikelihoodFit -t -1 --expectSignal 1 {datacard} -n _{name}_bkgPlusSig 
python ../../../../HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a fitDiagnostics_{name}_bkgPlusSig.root -g fitDiagnostics_{name}_bkgPlusSig_plots.root
python ../../printPulls.py fitDiagnostics_{name}_bkgPlusSig_plots.root
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, fake_mass=fake_mass, systematics=(0 if options.nosys else 1))
        script_file = os.path.join(output_dir, output_prefix + '_run_closureChecks.sh')
        with open(script_file, 'w') as f:
            f.write(script)
        
        st = os.stat(script_file)
        os.chmod(script_file, st.st_mode | stat.S_IEXEC)

        # Write small script for impacts
        script = """#! /bin/bash

# Run impacts
combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --doInitialFit --robustFit 1
combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 --robustFit 1 --doFits --parallel 10
combineTool.py -M Impacts -d {name}_combine_workspace.root -m 125 -o {name}_impacts.json
plotImpacts.py -i {name}_impacts.json -o {name}_impacts
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, fake_mass=fake_mass, systematics=(0 if options.nosys else 1))
        script_file = os.path.join(output_dir, output_prefix + '_run_impacts.sh')
        with open(script_file, 'w') as f:
            f.write(script)
        
        st = os.stat(script_file)
        os.chmod(script_file, st.st_mode | stat.S_IEXEC)

        # Write small script for postfit shapes
        script = """#! /bin/bash

# Run postfit
echo combine -M MaxLikelihoodFit {datacard} -n _{name}_postfit --saveNormalizations --saveShapes --saveWithUncertainties --preFitValue 0
combine -M MaxLikelihoodFit {datacard} -n _{name}_postfit --saveNormalizations --saveShapes --saveWithUncertainties --preFitValue 0 
PostFitShapes -d {datacard} -o postfit_shapes_{name}.root -f fitDiagnostics_{name}_postfit.root:fit_b --postfit --sampling
python ../../convertPostfitShapesForPlotIt.py -i postfit_shapes_{name}.root
./../../../HEPToolsFCNC/analysis_2017/plotIt/plotIt -o postfit_shapes_{name}_forPlotIt ../../postfit_plotIt_config_{coupling}.yml -y
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, fake_mass=fake_mass, systematics=(0 if options.nosys else 1), coupling=("Hut" if "Hut" in output_prefix else "Hct"))
        script_file = os.path.join(output_dir, output_prefix + '_run_postfit.sh')
        with open(script_file, 'w') as f:
            f.write(script)
        
        st = os.stat(script_file)
        os.chmod(script_file, st.st_mode | stat.S_IEXEC)

def CMSNamingConvention(syst):
    # Taken from https://twiki.cern.ch/twiki/bin/view/CMS/HiggsWG/HiggsCombinationConventions
    # systlist = ['jec', 'jer', 'elidiso', 'muidiso', 'jjbtag', 'pu', 'trigeff']
    return syst
    #if syst == 'jec':
    #    return 'CMS_scale_j'
    #elif syst == 'jer': 
    #    return 'CMS_res_j'
    #elif syst == 'elidiso': 
    #    return 'CMS_eff_e'
    #elif syst == 'muidiso': 
    #    return 'CMS_eff_mu'
    #elif any(x in syst for x in ['lf', 'hf', 'lfstats1', 'lfstats2', 'hfstats1', 'hfstats2', 'cferr1', 'cferr2']): 
    #    return 'CMS_btag_%s'%syst
    #elif syst == 'pu': 
    #    return 'CMS_pu'
    #elif syst == 'trigeff': 
    #    return 'CMS_eff_trigger'
    #elif syst == 'pdf':
    #    return 'pdf'
    #elif syst == 'scale':
    #    return 'QCDscale'
    #else:
    #    return syst
#
# main
#
if __name__ == '__main__':
    main()

