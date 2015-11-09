#!/bin/ksh
#
# NAME
#       proc_1_get_data_mars.ksh
#
# PURPOSE
#       ERA_data from MARS 
#       gets one month of data
#
# HISTORY
#       2012-05-11  A.Kniffka DWD KU22
#           created
#       2012-06-12 M. Jerg DWD KU22 modified to only extract MARS
#       2012-06-21 S. Stapelberg DWD KU22 some minor changes
#       2014-04-08 MJ migration to cca/sf7
#       2015-02-24 C. Schlundt: check data availability before ecp call
#

set -xv

#path configfile ausfuehren
. $1

#proc1 configfile ausfuehren
. $2

#name of grid info file
gridInfoFile=${3}

#name of remapping weights file
remapWeightsFile=${4}

# availability flag
aflag=-1

MM=$(printf %02d $STARTMONTH)

DATADIR=${INPUTDIR}/ERAinterim/${STARTYEAR}/${MM}

# check if data already on scratch
if [ -d $DATADIR ]; then
    echo "YES: $DATADIR exists"
    
    nfiles=$(ls $DATADIR/ERA_Interim*nc | wc -l)
    echo "Number of files: $nfiles"

        if [ $nfiles -gt 0 ]; then
            aflag=0
        fi
fi

# get data from MARS
if [ $aflag -ne 0 ]; then
    echo "No data available on scratch, get them now"
    
    echo "Create target directory: ${DATADIR}"
    mkdir -p $DATADIR
    
    # only create gridInfoFile if it doesn't exist yet
    if [[ ! -e ${gridInfoFile} ]] 	
    then
	echo "Create grid information file for remapping"
	Rscript ${ESA_ROUT}/write_ERA_gridinfo.R --vanilla ${lonIncr} ${latIncr} ${gridInfoFile}
    fi
    
    # get ERA interim
    DATE=${STARTYEAR}${MM}

    ${ESA_ROUT}/get_era_cci.ksh $STARTYEAR $MM $DATADIR $latIncr $lonIncr $gridInfoFile $remapWeightsFile
    retc=${?}
    
    if [ $retc -ne 0  ]; then 
        echo "GET_ERA_CCI FAILED: Not all files were retrieved for " ${DATE}"."
    fi
fi
