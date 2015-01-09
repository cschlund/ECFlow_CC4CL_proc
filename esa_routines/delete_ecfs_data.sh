#!/usr/bin/env bash

datestring=$1
ecfs=ec:/sf7/ESA_Cloud_cci_data/L3
backup=ec:/sf7/backup

# ec:/sf7/ESA_Cloud_cci_data/L3/200801

if [ $datestring ]; then 
    del=$(els $ecfs/$datestring/)
    echo "*** (1) remove tarfiles first ***"
    for i in $del; do erm $ecfs/$datestring/$i; done
    echo "*** (2) now remove date subfolders ***"
    ermdir $ecfs/$datestring
    echo "*** :-) FINISHED with $1 ***"
else 
    echo
    els -l $ecfs/
    echo
    echo "*** Give me a datestring <yyyymm> ***"
    echo
fi
