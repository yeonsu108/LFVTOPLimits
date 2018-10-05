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

def setNegativeBinsToZero(h, process):
    for i in range(1, h.GetNbinsX() + 1):
        if h.GetBinContent(i) < 0.:
            print 'Remove negative bin in TH1 %s for process %s'%(h.GetTitle(), process)
            h.SetBinContent(i, 0.)
    
def get_hist_regex(r):
    return '^%s(__.*(up|down))?$' % r


parser = argparse.ArgumentParser(description='Create shape datacards ready for combine')

parser.add_argument('-p', '--path', action='store', dest='root_path', type=str, default='/afs/cern.ch/work/b/brfranco/public/kTupleMaker/rootfiles/th1_with_syst_for_plotit/legacy/STFCNC01/', help='Directory containing rootfiles with the TH1 used for limit settings')
parser.add_argument('-l', '--luminosity', action='store', type=float, dest='luminosity', default=41500, help='Integrated luminosity (default is 41500 /pb)')
parser.add_argument('-o', '--output', action='store', dest='output', type=str, default='datacards', help='Output directory')
parser.add_argument('-c' , '--channel', action='store', dest='channel', type=str, default='all', help='Channel: el, mu, or all.')
parser.add_argument('-applyxsec' , action='store', dest='applyxsec', type=bool, default=True, help='Reweight MC processes by Xsec/Nevt from yml config.')
parser.add_argument('-xsecfile' , action='store', dest='xsecfile', type=str, default='xsec.yml', help='YAML config file path with Xsec and Nevt.')
parser.add_argument('--reweight', action='store_true', dest='reweight', help='Apply a preliminary reweighting. Not implemented yet.')
parser.add_argument('--fake-data', action='store_true', dest='fake_data', help='Use fake data instead of real data')
parser.add_argument('--SF', action='store_true', dest='SF', help='Produce cards for scale factors extraction (add line with rateParam). Not final yet!')
parser.add_argument('--nosys', action='store', dest='nosys', default=True, help='Consider or not systematic uncertainties (NB : bbb uncertainty is with another flag)')
parser.add_argument('--bbb', action='store', dest='bbb', default=False, help='Consider or not bin by bin MC stat systematic uncertainties')

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

DNN_Hct_hist_name = 'h_LepPt'
DNN_Hut_hist_name = 'h_LepPt'
channel = options.channel 
discriminant_categories = { # support regex (allow to avoid ambiguities if many histogram conatins same patterns)
        'DNN_Hct_b2j3': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hct_hist_name, channel_mapping[channel], selection_mapping['b2j3'])),
        'DNN_Hct_b2j4': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hct_hist_name, channel_mapping[channel], selection_mapping['b2j4'])),
        'DNN_Hct_b3j3': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hct_hist_name, channel_mapping[channel], selection_mapping['b3j3'])),
        'DNN_Hct_b3j4': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hct_hist_name, channel_mapping[channel], selection_mapping['b3j4'])),
        'DNN_Hct_b4j4': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hct_hist_name, channel_mapping[channel], selection_mapping['b4j4'])),
        'DNN_Hut_b2j3': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hut_hist_name, channel_mapping[channel], selection_mapping['b2j3'])),
        'DNN_Hut_b2j4': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hut_hist_name, channel_mapping[channel], selection_mapping['b2j4'])),
        'DNN_Hut_b3j3': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hut_hist_name, channel_mapping[channel], selection_mapping['b3j3'])),
        'DNN_Hut_b3j4': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hut_hist_name, channel_mapping[channel], selection_mapping['b3j4'])),
        'DNN_Hut_b4j4': get_hist_regex('{0}_{1}_{2}'.format(DNN_Hut_hist_name, channel_mapping[channel], selection_mapping['b4j4'])),
        #'yields': get_hist_regex('yields(?!(_sf|_df))'),
        }
        
discriminants = { # 'name of datacard' : list of tuple with (dicriminant ID, name above dictionary). Make sure the discriminantID ends with '_categoryName (for plot step)
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
    "DNN_Hut_allJetCategories" : [(1, 'DNN_Hut_b2j3'), (2, 'DNN_Hut_b2j4'), (3, 'DNN_Hut_b3j3'), (4, 'DNN_Hut_b3j4'), (5, 'DNN_Hut_b4j4')],
    }

processes_mapping = { # Dict with {key = human friendly name of your choice : value = regex to find rootfile} be carefull not to match too many files with the regex!
                      # Data !Must! contain 'data_%channels' in the name and MC must not data
        # Background
        'ttbb': ['TTpowhegttbb'],
        'SingleTop': ['.*SingleT.*'],
        # Signal
        'Hut': ['TTTH1L3BHut', 'STTH1L3BHut'],
        #'Hct': ['TTTH1L3BHct', 'STTH1L3BHct'],
        'Hct': ['STTH1L3BHct'],
        # Data
        'data_el' : ['SingleElectronRun2017'],
        'data_mu' : ['SingleMuonRun2017'],
        'data_all' : ['Single.*Run2017']
        }
processes_mapping['data_obs'] = processes_mapping['data_%s'%channel]

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
    #global options

    # get the options
    #options = get_options()

    signals = ['Hut', 'Hct']
    backgrounds = ['ttbb', 'SingleTop']

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
    if process != 'data_obs':
        histogram.Scale(options.luminosity)

    d = destination
    if not d:
        d = histogram.Clone()
        d.SetDirectory(ROOT.nullptr)
    else:
        d = destination
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

    print("Preparing ROOT file for combine...")

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

    # Create the list of histograms (nominal + systematics) for each category
    # we are interested in.
    # The key is the category name, and the value is a list of histogram. The list will always
    # contain at least one histogram (the nominal histogram), and possibly more, two per systematic (up & down variation)
    histogram_names = {}
    for category, histogram_name in categories_map.items():
        r = re.compile(histogram_name, re.IGNORECASE)
        f = ROOT.TFile.Open(processes_files.values()[0][0])
        histogram_names[category] = [n.GetName() for n in f.GetListOfKeys() if r.search(n.GetName())]
        f.Close()

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
                if options.applyxsec and not 'data' in process:
                    process_file_basename = os.path.basename(process_file)
                    xsec = xsec_data[process_file_basename]['cross-section']
                    nevt = xsec_data[process_file_basename]['generated-events']
                    TH1.Scale(xsec/float(nevt))
                if options.reweight :
                    print 'Reweighting on the flight not implemented yet! Exitting...'
                    sys.exit(1)
                    if "DY" in process_file :
                        if not ('DYJetsToLL_M-10to50') in process_file:
                            print "Reweight ", process_file, " by 0.75950" 
                            TH1.Scale(0.75950)
                shapes[category][process]['nominal'] = merge_histograms(process, TH1, dict_get(shapes[category][process], 'nominal'))
                if not process == "data_obs" : 
                    for systematic in systematics:
                        for variation in ['up', 'down']:
                            key = CMSNamingConvention(systematic) + variation.capitalize()
                            shapes[category][process][key] = merge_histograms(process, f.Get(original_histogram_name + '__' + systematic + variation), dict_get(shapes[category][process], key))
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

    import CombineHarvester.CombineTools.ch as ch
    root_path = options.root_path

    file, systematics = prepareFile(processes_mapping, discriminant_categories, root_path, discriminantName)
    
    for signal in signals :
        cb = ch.CombineHarvester()
        cb.AddObservations(['*'], [''], ['13TeV'], [''], discriminant)
        cb.AddProcesses(['*'], [''], ['13TeV_2017'], [''], backgrounds, discriminant, False)
        cb.AddProcesses(['*'], [''], ['13TeV_2017'], [''], [signal], discriminant, True)

        # Systematics
        if not options.nosys:
            for systematic in systematics:
                cb.cp().AddSyst(cb, systematic, 'shape', ch.SystMap()(1.00))
            cb.cp().AddSyst(cb, 'lumi_$ERA', 'lnN', ch.SystMap('era')(['13TeV_2017'], 1.027))
            #cb.cp().AddSyst(cb, '$PROCESS_xsec', 'lnN', ch.SystMap('process')
            #        (['ttbb'], 1.055842)
            #        )
        if options.SF :
            print "Background renormalization not finalized yet! Exitting..."
            sys.exit(1)
            cb.cp().AddSyst(cb, 'SF_$PROCESS', 'rateParam', ch.SystMap('process')
                    (['ttbb'], 1.)
                    )

        # Import shapes from ROOT file
        cb.cp().backgrounds().ExtractShapes(file, '$BIN/$PROCESS', '$BIN/$PROCESS__$SYSTEMATIC')
        cb.cp().signals().ExtractShapes(file, '$BIN/$PROCESS', '$BIN/$PROCESS__$SYSTEMATIC')

        # Bin by bin uncertainties
        if options.bbb:
            bbb = ch.BinByBinFactory()
            bbb.SetAddThreshold(0.1).SetMergeThreshold(0.5).SetFixNorm(True)
            bbb.MergeBinErrors(cb.cp().backgrounds())
            bbb.AddBinByBin(cb.cp().backgrounds(), cb)
            bbb.AddBinByBin(cb.cp().signals(), cb)

        if options.nosys and not options.bbb : 
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

# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {fake_mass} -o {workspace_root}
fi

# Run limit

echo combine -M AsymptoticLimits -n {name} {workspace_root} -S {systematics} --rMax 30000 --run expected #-v +2
combine -M AsymptoticLimits -n {name} {workspace_root} -S {systematics} --rMax 30000 --run expected #-v +2
#combine -H ProfileLikelihood -M AsymptoticLimits -n {name} {workspace_root} -S {systematics} --rMax 30000 --run expected
#combine -H ProfileLikelihood -M HybridNew -n {name} {workspace_root} -S {systematics} --testStat LHC --expectedFromGrid 0.5 
#combine -H ProfileLikelihood -M HybridNew -n {name} {workspace_root} -S {systematics} --testStat LHC --expectedFromGrid 0.84 
#combine -H ProfileLikelihood -M HybridNew -n {name} {workspace_root} -S {systematics} --testStat LHC --expectedFromGrid 0.16 
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, fake_mass=fake_mass, systematics=(0 if options.nosys else 1))
        script_file = os.path.join(output_dir, output_prefix + '_run_limits.sh')
        with open(script_file, 'w') as f:
            f.write(script)
        
        st = os.stat(script_file)
        os.chmod(script_file, st.st_mode | stat.S_IEXEC)

def CMSNamingConvention(syst):
    # Taken from https://twiki.cern.ch/twiki/bin/view/CMS/HiggsWG/HiggsCombinationConventions
    # systlist = ['jec', 'jer', 'elidiso', 'muidiso', 'jjbtag', 'pu', 'trigeff']
    if syst == 'jec':
        return 'CMS_scale_j'
    elif syst == 'jer': 
        return 'CMS_res_j'
    elif syst == 'elidiso': 
        return 'CMS_eff_e'
    elif syst == 'muidiso': 
        return 'CMS_eff_mu'
    elif any(x in syst for x in ['lf', 'hf', 'lfstats1', 'lfstats2', 'hfstats1', 'hfstats2', 'cferr1', 'cferr2']): 
        return 'CMS_btag_%s'%syst
    elif syst == 'pu': 
        return 'CMS_pu'
    elif syst == 'trigeff': 
        return 'CMS_eff_trigger'
    elif syst == 'pdf':
        return 'pdf'
    elif syst == 'scale':
        return 'QCDscale'
    else:
        return syst
#
# main
#
if __name__ == '__main__':
    main()

