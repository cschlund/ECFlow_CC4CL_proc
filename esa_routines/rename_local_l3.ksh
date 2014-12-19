#!/bin/ksh
#
# Rename local L3 files
#
#
# written 2013-03-01  M. Jerg
# 2014-04-08 MJ migration to cca/sf7
# 
# 
############################
#
#          Main
#
############################

set -x

# source path configfile
. $1

cd ${l3outputpath}/

substring=42N53N00E18E

set -A dumm `find . -type f -name "*.nc"`

START=$(date +%s)

count=1
for file2cp in ${dumm[*]} ; do

    lrm=0

    base=`basename ${file2cp}`
    path=`dirname ${file2cp}` 

    # in case the file was already renamed do not rename again lrm=0
    case $base in 
        *"$substring"*) lrm=0 ;; 
        *) lrm=1 ;; 
    esac 

    # if file has not been renamed yet, rename lrm=1  
    if [ ${lrm} -eq 1 ] 
    then 
        echo 'yes' $lrm $base $path 
        case $path in 
            *"$substring"*) mv ${file2cp} ${path}/${substring}_${base} ;; 
            *) echo 'Nothing to do' $file2cp ;; 
        esac 
    else 
        echo 'no' $lrm $base $path 
    fi 

done

#cd ${basedir}

#end
