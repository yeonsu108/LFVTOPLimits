#!/usr/bin/env python
import CombineHarvester.CombineTools.ch as ch
import ROOT
import argparse
import math

# Example usage:
# python partialCorrelationEdit.py datacard.txt -m 125 \
# --process jes_1,0.5:jes_2,0.75 \
# --postfix-uncorr _2016 \
# --output-txt new_datacard.txt --output-root new_datacard.root
#
# Notes:
#  - The assumption is that the "jes_1" and "jes_2" are the names used in some other card
#    that we want to be partially correlated with the coresponding uncertainties in this card.
#    In other words: we start from the fully correlated configuration.
#  - Should only be used with lnN/shape uncertainties and non-parametric models
#  - Currently only supports positive correlations and simple decorrelation of two parameters
#  - It is essential to verify the output of this script carefully:
#      * that without supplying any --process option an identical card is produced yielding
#        the same fit result (sanity check that the CH processing was ok)
#      * after the splitting, fitting the same card should yield ~roughly the same fit result.
#        it will not be perfect because we treat all effects as if they are Guassian, which they
#        are not.


def Split(cb, name, year_list, correlation):
    cb_syst = cb.cp().syst_name([name])
    print '>> The following systematics will be cloned and adjusted:'
    cb_syst.PrintSysts()
    if len(year_list) == 2:
        # Assume that the name is in CMS_source form FIXME
        ch.CloneSysts(cb_syst, cb, lambda p : p.set_name('CMS_' + year_list[0] + '_' + str(name.split('_')[1])))
        ch.CloneSysts(cb_syst, cb, lambda p : p.set_name('CMS_' + year_list[1] + '_' + str(name.split('_')[1])))
    cb_syst.syst_name([name], False)
    #cb_syst.PrintSysts()

ROOT.gSystem.Load('libHiggsAnalysisCombinedLimit')

cb = ch.CombineHarvester()
cb.SetFlag('workspace-uuid-recycle', True)
cb.SetFlag('workspaces-use-clone', True)
cb.SetFlag('import-parameter-err', False)
cb.SetFlag("zero-negative-bins-on-import", False)
cb.SetFlag("check-negative-bins-on-import", False)

parser = argparse.ArgumentParser()

parser.add_argument('datacard', help='datacard to edit')
parser.add_argument('-m', '--mass', help='mass value', default='120')
parser.add_argument('--process', default='', help='List of nuisances to process and desired correlation coeffs: [name],[correlation]:...')
parser.add_argument('--output-txt', default='decorrelated_card.txt')
parser.add_argument('--output-root', default='decorrelated_card.shapes.root')
args = parser.parse_args()

cb.ParseDatacard(args.datacard, mass=args.mass)

if args.process != '':
    actions = [X.split(',') for X in args.process.split(':')]
    
    for name, correlation, year in actions:
        print name, correlation, year
        year_list = year.split('-')
        print '>> Setting correlation coefficient of %s to %f' % (name, float(correlation))
        Split(cb, name, year_list, float(correlation))
    cb.syst_name([name], False)
    #cb.PrintSysts() #check if implementation is done correctly

print '>> Writing new card and ROOT file: %s' % ((args.output_txt, args.output_root),)
cb.WriteDatacard(args.output_txt, args.output_root)
