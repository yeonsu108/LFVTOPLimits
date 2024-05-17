import ROOT

# own style options:
divideByBinWidth = False
# divideByBinWidth = True
minimumOne = True
additionalPoissonUncertainty = False


def defaultStyle():
    st = ROOT.TStyle("defaultStyle", "Sebastian's owns style")
    st.SetCanvasColor(ROOT.kWhite)
    st.SetCanvasBorderMode(0)
    st.SetFrameBorderMode(0)
    st.SetCanvasDefH(800)
    st.SetCanvasDefW(800)

    st.SetPadTickX(1)
    st.SetPadTickY(1)

    st.SetPadColor(ROOT.kWhite)

    # Margins:
    st.SetPadTopMargin(0.06)
    st.SetPadBottomMargin(0.12)
    st.SetPadLeftMargin(0.16)
    st.SetPadRightMargin(0.04)

    st.SetTitleFillColor(ROOT.kWhite)
    st.SetTitleBorderSize(0)

    # st.SetTitleOffset(1.1, "x")
    st.SetTitleOffset(1.0, "x")
    # st.SetTitleOffset(1.6, "y")
    st.SetTitleOffset(1.3, "y")

    st.SetStatBorderSize(1)
    st.SetStatColor(0)

    st.SetLegendBorderSize(0)
    st.SetLegendFillColor(ROOT.kWhite)
    st.SetLegendFont(st.GetLabelFont())
    # st.SetLegendTextSize( st.GetLabelSize() ) not in current ROOT version

    st.SetOptStat(0)

    # textSize = 0.05
    # st.SetLabelSize(textSize, "xyz")
    # st.SetTitleSize(textSize, "xyz")
    # st.SetLabelSize(textSize, "xyz")
    st.SetLabelSize(0.04, "xyz")
    # st.SetTitleSize(0.04, "xyz")
    st.SetTitleSize(0.055, "xyz")

    st.SetTextFont(st.GetLabelFont())
    # st.SetTextSize(st.GetLabelSize())
    st.SetTextSize(0.05)

    # st.SetNdivisions(505, "xyz")
    st.SetNdivisions(510, "xyz")
    ROOT.TGaxis.SetMaxDigits(4)

    st.SetTickLength(0.03, "XYZ")
    st.SetStripDecimals(ROOT.kTRUE)
    st.SetLabelOffset(0.007, "XYZ")
    # st.SetLegendTextSize(0.02)

    st.SetPalette(56)
    st.SetNumberContours(999)

    # st.SetErrorX(1)
    # st.SetErrorX(0)

    st.cd()
    return st


def style2d():
    st = defaultStyle()
    st.SetPadRightMargin(0.19)
    # st.SetTitleOffset(1.35, "z")
    st.SetTitleOffset(1.15, "z")
    return st
def style1d():
    st = defaultStyle()
    # st.SetPadRightMargin(0.19)
    # st.SetTitleOffset(1.35, "z")
    return st


def setPaletteRWB():
    # Sets the current palette to red -> white -> blue
    from array import array
    steps = array('d', [0.0, 0.5, 1.0])
    red = array('d', [1.0, 1.0, 0.0])
    green = array('d', [0.0, 1.0, 0.0])
    blue = array('d', [0.0, 1.0, 1.0])
    ROOT.TColor.CreateGradientColorTable(
        len(steps), steps, red, green, blue, ROOT.gStyle.GetNumberContours())


def setPaletteBWR():
    # Sets the current palette to blue -> white -> red
    from array import array
    steps = array('d', [0.0, 0.5, 1.0])
    red = array('d', [0.0, 1.0, 1.0])
    green = array('d', [0.0, 1.0, 0.0])
    blue = array('d', [1.0, 1.0, 0.0])
    ROOT.TColor.CreateGradientColorTable(
        len(steps), steps, red, green, blue, ROOT.gStyle.GetNumberContours())

def setPalette(styletype):
    from array import array
    NRGBs = 9
    NCont = 255
    stops = [0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000]

    if styletype=="bird":
        # #Bird
        red   = [ 0.2082, 0.0592, 0.0780, 0.0232, 0.1802, 0.5301, 0.8186, 0.9956, 0.9764]
        green = [ 0.1664, 0.3599, 0.5041, 0.6419, 0.7178, 0.7492, 0.7328, 0.7862, 0.9832]
        blue  = [ 0.5293, 0.8684, 0.8385, 0.7914, 0.6425, 0.4662, 0.3499, 0.1968, 0.0539]
    elif styletype=="light":
        #Light Temperature
        red   = [  31./255.,  71./255., 123./255., 160./255., 210./255., 222./255., 214./255., 199./255., 183./255.]
        green = [  40./255., 117./255., 171./255., 211./255., 231./255., 220./255., 190./255., 132./255.,  65./255.]
        blue  = [ 234./255., 214./255., 228./255., 222./255., 210./255., 160./255., 105./255.,  60./255.,  34./255.]
    elif styletype=="rainbow":
        # #Rainbow
        red   = [  0./255.,   5./255.,  15./255.,  35./255., 102./255., 196./255., 208./255., 199./255., 110./255.]
        green = [  0./255.,  48./255., 124./255., 192./255., 206./255., 226./255.,  97./255.,  16./255.,   0./255.]
        blue  = [ 99./255., 142./255., 198./255., 201./255.,  90./255.,  22./255.,  13./255.,   8./255.,   2./255.]
    elif styletype=="pastel":
        # #Pastel
        red   = [ 180./255., 190./255., 209./255., 223./255., 204./255., 228./255., 205./255., 152./255.,  91./255.]
        green = [  93./255., 125./255., 147./255., 172./255., 181./255., 224./255., 233./255., 198./255., 158./255.]
        blue  = [ 236./255., 218./255., 160./255., 133./255., 114./255., 132./255., 162./255., 220./255., 218./255.]
    elif styletype=="cool":
        # #Cool
        red   = [  33./255.,  31./255.,  42./255.,  68./255.,  86./255., 111./255., 141./255., 172./255., 227./255.]
        green = [ 255./255., 175./255., 145./255., 106./255.,  88./255.,  55./255.,  15./255.,   0./255.,   0./255.]
        blue  = [ 255./255., 205./255., 202./255., 203./255., 208./255., 205./255., 203./255., 206./255., 231./255.]
    else:
        #Light Temperature
        red   = [  31./255.,  71./255., 123./255., 160./255., 210./255., 222./255., 214./255., 199./255., 183./255.]
        green = [  40./255., 117./255., 171./255., 211./255., 231./255., 220./255., 190./255., 132./255.,  65./255.]
        blue  = [ 234./255., 214./255., 228./255., 222./255., 210./255., 160./255., 105./255.,  60./255.,  34./255.]

    s = array('d', stops)
    r = array('d', red)
    g = array('d', green)
    b = array('d', blue)
    ROOT.TColor.CreateGradientColorTable(NRGBs, s, r, g, b, NCont)
    ROOT.gStyle.SetNumberContours(NCont)


defaultStyle()

# not style, but similar
ROOT.gROOT.SetBatch()
ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.ForceStyle()

