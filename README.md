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
First extract envelope of the systematics for which it is necessary
`python makeEnvelope.py -p /path/to/your/rootfiles`
Write the datacards and rootfiles suitable for combine
`python prepareShapesAndCards.py -p /path/to/your/rootfiles`
Run combine to extract the limits
`python run_all_limits.py`
Plot the limits
`python plotLimitsPerCategory.py`

All these python scripts are easily configurable, check what you can do with the `--help` option
