# FCNCLimits
Toolbox to derive upper limits for 2017/2018 FCNC tH(bb) analysis
# Installation
```
export SCRAM_ARCH=slc6_amd64_gcc530
cmsrel CMSSW_8_1_0
cd CMSSW_8_1_0/src 
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v7.0.11
cd -
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
mkdir UserCode
git clone https://github.com/BrieucF/FCNCLimits UserCode/FCNCLimits
scramv1 b clean; scramv1 b
```
# Stay up to date
You can check that the above recipe is up to date by following the links
https://cms-hcomb.gitbooks.io/combine/content/part1/#for-end-users-that-dont-need-to-commit-or-do-any-development
and
http://cms-analysis.github.io/CombineHarvester/index.html#getting-started

# Run the limits
If not done earlier (now we do it before limit setting step), extract envelope of the systematics for which it is necessary

`python makeEnvelope.py -p /path/to/your/rootfiles`

Write the datacards and rootfiles suitable for combine (be careful that cross sections and sum of event weights are taken from `xsec.yml` and that for signal cross section is different than the one used in `plotIt`!)

`python prepareShapesAndCards.py -p /path/to/your/rootfiles`

Run combine to extract the limits

`python run_all_limits.py`

Plot the limits and print the values extrapolated to branching ratios

`python plotLimitsPerCategory.py`

All these python scripts are easily configurable, check what you can do with the `--help` option

To see how to do postfit plots, nuisance pulls, impacts, etc, have a look at the file: `run_everything_for2018.sh`

You can also print limits in form of latex table with `printLimitLatexTable.py`

# To pay attention to

The signal cross section you use in 'xsec.yml' has to be propagated to `plotLimitsPerCategory.py` and to `printLimitLatexTable.py`. Note that `plotLimitsPerCategory.py` also needs the real, physical, expected signal cross section (for coupling one) to derive the limit on branching ratio.

