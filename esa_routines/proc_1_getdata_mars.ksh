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
#

set -xv

#path configfile ausfuehren
. $1

#proc1 configfile ausfuehren
. $2


unix_start=`${ESA_ROUT}/ymdhms2unix.ksh $STARTYEAR $STARTMONTH $STARTDAY`

if [ $STOPDAY -eq 0 ] ; then 
    STOPDAY=`cal $STOPMONTH $STOPYEAR | tr -s " " "\n" | tail -1` # nr days of month
fi

unix_stop=`${ESA_ROUT}/ymdhms2unix.ksh $STOPYEAR $STOPMONTH $STOPDAY`
unix_counter=$unix_start

while [ $unix_counter -le $unix_stop ]; do 

    YEAR=`perl -e 'use POSIX qw(strftime); print strftime "%Y",localtime('$unix_counter');'`
    MONS=`perl -e 'use POSIX qw(strftime); print strftime "%m",localtime('$unix_counter');'`
    DAYS=`perl -e 'use POSIX qw(strftime); print strftime "%d",localtime('$unix_counter');'`

    DATADIRE=${INPUTDIR}/ERAinterim/${YEAR}/${MONS}/${DAYS} # new subdir days
    mkdir -p $DATADIRE
    #get ERA interim by the day
    DATE=${YEAR}${MONS}${DAYS}

    ${ESA_ROUT}/get_era_cci.ksh $DATE $DATADIRE
    retc=${?}

    if [ $retc -ne 0  ]; then 
        echo "GET_ERA_CCI FAILED: Not all files were retrieved for " ${DATE}"."
    fi

    # go to next day
    (( unix_counter += 86400 ))

done
# END
