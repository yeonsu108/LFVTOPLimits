import os, sys, argparse, json
import ROOT

parser = argparse.ArgumentParser(description='Store limits inside a json file and plot them if required (one bin per category).')
parser.add_argument('-limitfolder', dest='limitfolder', default='./datacards', type=str, help='Folder where Hct and Hut combine output folders are stored')
parser.add_argument('-verbose', dest='verbose', type=bool, default=False, help='Dump limits to stdout or not.')
parser.add_argument('-doPlot', dest='doPlot', type=bool, default=True, help='Do the limit plot or not.')
parser.add_argument('-category_order', dest='category_order', nargs='+', default=['b2j3', 'b2j4', 'b3j3', 'b4j4', 'all'], help='Bin order in the limit plot, names must be the same then in the combine rootfile: e.g. higgsCombine*_b3j3*.root.')
parser.add_argument('-bin_labels', dest='category_labels', nargs='+', default=['b2j3', 'b2j4', 'b3j3', 'b4j4', 'all'], help='Use this option if you want to modify the x-axis labels. Must be same order and length then -category_order argument.')
parser.add_argument('-unblind', dest='unblind', type=bool, default=False, help='Display or not the observed limit.')

options = parser.parse_args()

ROOT.gROOT.SetBatch()

def getLimitsFromFile(input_file):
    """
    Extract observed, expected, and 1/2 sigma limits from combine output rootfile
    """
    f = ROOT.TFile.Open(input_file)
    if not f or f.IsZombie() or f.TestBit(ROOT.TFile.kRecovered):
        return None

    data = {}
    # Index 0 is DOWN error, index 1 is UP error
    one_sigma = data.setdefault('one_sigma', [0, 0])
    two_sigma = data.setdefault('two_sigma', [0, 0])

    limit = f.Get('limit')

    limit.GetEntry(2)
    data['expected'] = limit.limit

    limit.GetEntry(5)
    data['observed'] = limit.limit

    limit.GetEntry(4)
    two_sigma[1] = limit.limit
    #two_sigma[1] = limit.limit - data['expected']

    limit.GetEntry(0)
    #two_sigma[0] = data['expected'] - limit.limit
    two_sigma[0] = limit.limit

    limit.GetEntry(3)
    #one_sigma[1] = limit.limit - data['expected']
    one_sigma[1] = limit.limit

    limit.GetEntry(1)
    #one_sigma[0] = data['expected'] - limit.limit
    one_sigma[0] = limit.limit

    return data

def add_labels(canvas, additional_label='', lumi='41.5', energy='13', cms='Work in progress'):
    latexLabel = ROOT.TLatex()
    latexLabel.SetTextSize(0.75 * canvas.GetTopMargin())
    latexLabel.SetNDC()
    latexLabel.SetTextFont(42) # helvetica
    latexLabel.DrawLatex(0.69, 0.96, lumi + ' fb^{-1} (%s TeV)'%energy)
    latexLabel.SetTextFont(61) # helvetica bold face
    latexLabel.SetTextSize(1.15 * canvas.GetTopMargin())
    latexLabel.DrawLatex(0.78, 0.85, additional_label)
    latexLabel.SetTextSize(0.75 * canvas.GetTopMargin())
    latexLabel.DrawLatex(0.13, 0.96, "CMS")
    latexLabel.SetTextFont(52) # helvetica italics
    latexLabel.DrawLatex(0.22, 0.96, cms)


def plot_limits(signal_name, limit_dict, legend_position=[0.2, 0.7, 0.65, 0.9]):
    nBins = len(limit_dict)
    bin_low_edges = array('d', range(nBins+1))
    #canvas = ROOT.TCanvas(signal_name + "_limits_per_category", signal_name + "_limits_per_category", 600, 450)
    canvas = ROOT.TCanvas(signal_name + "_limits_per_category", signal_name + "_limits_per_category")
    th1_for_canvas_layout = ROOT.TH1F("bla", "bla", nBins, bin_low_edges)
    th1_for_canvas_layout.SetLineColorAlpha(ROOT.kWhite, 0)
    xAxis = th1_for_canvas_layout.GetXaxis()
    xAxis.CenterLabels()
    xAxis.SetLabelSize(0.07)
    xAxis.SetLabelFont(42)
    xAxis.SetTitleFont(42)
    yAxis = th1_for_canvas_layout.GetYaxis()
    yAxis.SetNdivisions(010)
    yAxis.SetTitle("95% CL upper limit on #sigma #times BR [pb]")
    yAxis.SetLabelFont(42)
    yAxis.SetTitleFont(42)
    yAxis.SetTitleSize(0.039)
    expected_lines = {}
    observed_lines = {}
    one_sigma_rectangles = {}
    two_sigma_rectangles = {}
    for category_binNumber in range(len(options.category_order)):
        category = options.category_order[category_binNumber]
        if category in limit_dict.keys():
            categ_limits = limit_dict[category]
            xAxis.SetBinLabel(category_binNumber+1, options.category_labels[category_binNumber])
            th1_for_canvas_layout.SetBinContent(category_binNumber+1, categ_limits['two_sigma'][1]*1.5)
    th1_for_canvas_layout.Draw()
    for category_binNumber in range(len(options.category_order)):
        category = options.category_order[category_binNumber]
        if category in limit_dict.keys():
            categ_limits = limit_dict[category]
            xlow = xAxis.GetBinLowEdge(category_binNumber+1)
            xup = xAxis.GetBinUpEdge(category_binNumber+1)
            one_sigma_up = categ_limits['one_sigma'][1]
            one_sigma_down = categ_limits['one_sigma'][0]
            two_sigma_up = categ_limits['two_sigma'][1]
            two_sigma_down = categ_limits['two_sigma'][0]
            expected_lines[category] = ROOT.TLine(xlow, categ_limits['expected'], xup, categ_limits['expected'])
            expected_lines[category].SetLineStyle(7)
            expected_lines[category].SetLineWidth(2)
            observed_lines[category] = ROOT.TLine(xlow, categ_limits['observed'], xup, categ_limits['observed'])
            observed_lines[category].SetLineWidth(2)
            if not options.unblind:
                observed_lines[category].SetLineColorAlpha(ROOT.kWhite, 0)
            one_sigma_rectangles[category] = ROOT.TPolyLine(4, array('d', [xlow, xup, xup, xlow]), array('d',[one_sigma_down, one_sigma_down, one_sigma_up, one_sigma_up] ))
            one_sigma_rectangles[category].SetFillColor(3)
            one_sigma_rectangles[category].SetLineColor(3)
            two_sigma_rectangles[category] = ROOT.TPolyLine(4, array('d', [xlow, xup, xup, xlow]), array('d',[two_sigma_down, two_sigma_down, two_sigma_up, two_sigma_up] ))
            two_sigma_rectangles[category].SetFillColor(5)
            two_sigma_rectangles[category].SetLineColor(5)
            two_sigma_rectangles[category].Draw('f same')
            one_sigma_rectangles[category].Draw('f same')
            expected_lines[category].Draw('same')
            observed_lines[category].Draw('same')
    # Legend
    legend = ROOT.TLegend(legend_position[0], legend_position[1], legend_position[2], legend_position[3], "95% CL upper limits")
    legend.SetTextFont(42)
    legend.SetFillStyle(0)
    legend.SetFillColor(ROOT.kWhite)
    legend.SetLineColor(ROOT.kWhite)
    legend.SetShadowColor(ROOT.kWhite)
    legend.AddEntry(expected_lines[limit_dict.keys()[0]], 'Expected', 'l')
    legend.AddEntry(one_sigma_rectangles[limit_dict.keys()[0]], 'Expected #pm 1 std. deviation', 'f')
    legend.AddEntry(two_sigma_rectangles[limit_dict.keys()[0]], 'Expected #pm 2 std. deviations', 'f')
    legend.AddEntry(observed_lines[limit_dict.keys()[0]], 'Observed', 'l')
    legend.Draw('same')
    add_labels(canvas, signal_name)
    canvas.Print(os.path.join(options.limitfolder, signal_name + '_limits.pdf'))
    canvas.Print(os.path.join(options.limitfolder, signal_name + '_limits.png'))
    canvas.SetLogy()
    canvas.Print(os.path.join(options.limitfolder, signal_name + '_limits_log.pdf'))
    canvas.Print(os.path.join(options.limitfolder, signal_name + '_limits_log.png'))


signal_folders = [folder for folder in os.listdir(options.limitfolder) if os.path.isdir(os.path.join(options.limitfolder, folder))]
if not signal_folders:
    print "Found no folder inside %s"%options.limitfolder
    sys.exit(1)

for signal_folder in signal_folders:
    print "Extracting limits for %s"%signal_folder
    signal_folder_path = os.path.join(options.limitfolder, signal_folder)
    limit_rootfiles = [rootfile for rootfile in os.listdir(signal_folder_path) if rootfile.startswith('higgsCombine')]
    #categories = [] # [rootfilename.split('.')[0].split('_')[-1] for rootfilename in limit_rootfiles]
    dict_cat_limits = {}
    for category in options.category_order:
        found_category = False
        for limit_rootfile in limit_rootfiles:
            limit_rootfile_path = os.path.join(signal_folder_path, limit_rootfile)
            category_tmp = limit_rootfile.split('.')[0].split('_')[-1]
            if category_tmp == category:
                if found_category:
                    print "Error: two rootfiles match category name %s in %s, don't know which one to choose. Please move one of them."%(category, signal_folder_path)
                    sys.exit(1)
                found_category = True
                limits = getLimitsFromFile(limit_rootfile_path)
                dict_cat_limits[category] = limits
        if not found_category:
            print "Warning: I do not find rootfile for category %s in %s. The code assumes rootfile name of the form e.g. higgsCombine*_b3j3*.root without underscore after category name."%(category, signal_folder_path)
    json_limit_filepath = os.path.join(signal_folder_path, signal_folder + '_limits.json')
    if options.verbose:
        print json.dumps(dict_cat_limits, indent=4)
    with open(json_limit_filepath, 'w') as limit_json:
        json.dump(dict_cat_limits, limit_json)
    print "%s written with limits inside"%json_limit_filepath

    if options.doPlot:
        from array import array
        ROOT.gROOT.ProcessLine(".x setTDRStyle.C")
        plot_limits(signal_folder, dict_cat_limits)






