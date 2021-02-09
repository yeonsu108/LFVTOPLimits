#!/bin/bash
export PYTHONPATH=`echo $PYTHONPATH | sed -e 's/:\/cvmfs\/cms\.cern\.ch\/slc6_amd64_gcc530\/external\/py2-pandas\/0\.17\.1-giojec7\/lib\/python2\.7\/site-packages//'`

export PYTHONPATH=/home/minerva1993/CMSSW_8_1_0/external/py2_install/lib/python2.7/site-packages:$PYTHONPATH
