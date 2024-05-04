#postfix=$1
postfix=0501_symm1

source run_everything_oneYear.sh datacards_2018_${postfix} 2018
source run_everything_oneYear.sh datacards_2017_${postfix} 2017
source run_everything_oneYear.sh datacards_2016post_${postfix} 2016post
source run_everything_oneYear.sh datacards_2016pre_${postfix} 2016pre
