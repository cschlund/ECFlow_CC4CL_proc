#!/bin/ksh
#
# proc_1_get_data_mars.ksh
#
#***
#
# ######################################################################################################
#
# NAME
#       proc_1_get_data_mars.ksh
#
# PURPOSE
#       ERA_data from MARS 
#       gets one month of data
#
# USES
#       
#       
#
# HISTORY
#       2012-05-11  A.Kniffka DWD KU22
#           created
#       2012-06-12 M. Jerg DWD KU22 modified to only extract MARS
#       2012-06-21 S. Stapelberg DWD KU22 some minor changes
# 2014-04-08 MJ migration to cca/sf7
#
# ######################################################################################################

############################
#
#          Main
#
############################

set -xv

#path configfile ausfuehren
. $1

#proc1 configfile ausfuehren
. $2

# changed to unixseconds sstapelb 21-06-2012
unix_start=`${ESA_ROUT}/ymdhms2unix.ksh $STARTYEAR $STARTMONTH $STARTDAY`
if [ $STOPDAY -eq 0 ] ; then
STOPDAY=`cal $STOPMONTH $STOPYEAR | tr -s " " "\n" | tail -1` # nr days of month
fi
unix_stop=`${ESA_ROUT}/ymdhms2unix.ksh $STOPYEAR $STOPMONTH $STOPDAY`
unix_counter=$unix_start

while [ $unix_counter -le $unix_stop ]
  do
    YEAR=`perl -e 'use POSIX qw(strftime); print strftime "%Y",localtime('$unix_counter');'`
    MONS=`perl -e 'use POSIX qw(strftime); print strftime "%m",localtime('$unix_counter');'`
    DAYS=`perl -e 'use POSIX qw(strftime); print strftime "%d",localtime('$unix_counter');'`
    DATADIRE=${INPUTDIR}/ERAinterim/${YEAR}/${MONS}/${DAYS} # new subdir days
    mkdir -p $DATADIRE
    #get ERA interim by the day
    DATE=${YEAR}${MONS}${DAYS}
    ${ESA_ROUT}/get_era_cci.ksh $DATE $DATADIRE
    retc=${?}
    if [ $retc -ne 0  ]
	then
	echo "GET_ERA_CCI FAILED: Not all files were retrieved for " ${DATE}"."
    fi
    (( unix_counter += 86400 )) # go to next day
done
# END

# #set proper start and end time
# YEAR=$STARTYEAR
# MON=1
# if [ $YEAR -eq $STARTYEAR ]
#     then
#     MON=$STARTMONTH
# fi
# 
# STOPM=12
# if [ $YEAR -eq $STOPYEAR ]
#     then
#     STOPM=$STOPMONTH
# fi
# 
# #loop over months
# while [ $MON -le $STOPM ] 
#   do
#   MONS=$MON
#   if [ $MON -lt 10 ]
#       then
#       MONS=0$MON
#   fi
#   echo $MON
# 
#   #changed by sstapelb-21062012--------------------------
#   DAY_stop=`cal $MONS $YEAR | tr -s " " "\n" | tail -1` # nr days of month
#   for DAYS in `seq -w 1 $DAY_stop`:
#     do
#     DATADIRE=${INPUTDIR}/ERAinterim/${YEAR}/${MONS}/${DAYS} # new subdir days
#     mkdir -p $DATADIRE
#     #get ERA interim by the day
#     DATE=${YEAR}${MONS}${DAYS}
#     ${ESA_ROUT}/get_era_cci.ksh $DATE $DATADIRE
#     retc=${?}
#   done #loop day
#   #------------------------------------------------------
#   MON=$(( $MON+1 ))
# done #loop month
# END

# 
#   #set directory where the stuff is to be put
#   DATADIRE=${INPUTDIR}/ERAinterim/${YEAR}/${MONS}
#   #make directories if necessary
#   mkdir -p $DATADIRE
# 
#   DAY_stop=`days_in_month $MONS $YEAR`
# # DAY_stop=1
#   DAY=1
#   while [ $DAY -le $DAY_stop ] 
#     do
#     DAYS=$DAY
#     if [ $DAY -lt 10 ]
# 	then
# 	DAYS=0$DAY
#     fi
# 
# #get ERA interim by the day
#     DATE=${YEAR}${MONS}${DAYS}
#     ${ESA_ROUT}/get_era_cci.ksh $DATE $DATADIRE
#     retc=${?}
#     
#     DAY=$(( $DAY+1 ))
#   done #loop day
#   MON=$(( $MON+1 ))
# done #loop month
# 
# # END
