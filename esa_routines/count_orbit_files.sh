#!/usr/bin/env bash
#
# count orbit files for processing
#

# source config_paths.file
. $1
# source config_proc_1_getdata_avhrr.file
# source config_proc_1_getdata_modis.file
. $2
# PROCDAY
procday=$3


if [ $procday -ge 0 ]; then 

    day=$(printf %02d $procday)

    month=$(printf %02d $STARTMONTH)
    
    if [ $instrument == 'AVHRR' ]; then 
    
        # count all files
        numfil=$(ls $INPUTDIR/$instrument/$platform/$STARTYEAR/$month/$day/*/*.h5 |wc -l)
        # divide $numfil by 3: *avhrr*, *sunsatangles*, *qualflags* files
        cnt=`perl -e 'print '$numfil'/3;'`
    
    else
    
        # MODIS
        # count all files
        numfil=$(ls $INPUTDIR/$instrument/$platform/$STARTYEAR/$month/$day/*.hdf |wc -l)
        # divide by 2
        cnt=`perl -e 'print '$numfil'/2;'`
    
    fi

else

    month=$(printf %02d $STARTMONTH)
    
    if [ $instrument == 'AVHRR' ]; then 
    
        # count all files
        numfil=$(ls $INPUTDIR/$instrument/$platform/$STARTYEAR/$month/*/*/*.h5 |wc -l)
        # divide $numfil by 3: *avhrr*, *sunsatangles*, *qualflags* files
        cnt=`perl -e 'print '$numfil'/3;'`
    
    else
    
        # MODIS
        # count all files
        numfil=$(ls $INPUTDIR/$instrument/$platform/$STARTYEAR/$month/*/*.hdf |wc -l)
        # divide by 2
        cnt=`perl -e 'print '$numfil'/2;'`
    
    fi

fi

echo $cnt
