#!/bin/ksh
#
# ###########################################################################################
#
# NAME
#       ymdhms2unix.ksh
#
# PURPOSE
#       Converts date "Year Month Day Hour Minute Seconds" to unixseconds w/o using date -d
#
# USAGE
#       ./ymdhms2unix Year Month Day Hour Minute Seconds
#
# Description
#       Same as date -d "Year/Month/Day Hour:Minute:Seconds" +%s on GNU linux machines
#       but works also on non GNU machines (Solaris, AIX) like in Reading ECMWF
#
# HISTORY
#       21-06-2012 S. Stapelberg KU22 DWD
#         Based on a script found in the internet.
#         Changed Input and Type of Output
#         Added necessary doy function w/o date
#         Added defaults
#       22-06-2012 S. Stapelberg KU22 DWD 
#         Bug fix in leapyear function (Year 2000 is a leap year!!)
#
# ###########################################################################################

#-----------------------------------------------------------------------------
function doy {

# Calculates the day of year
# ARG1 Year
# ARG2 Month
# ARG3 Day

  if [ $2 -ne 1 ] 
  then 
    for i in `seq 1 $(($2 -1))`
    do
      (( days += `cal $i $1  |tr -s " " "\n"|tail -1`)) #nr days of month
    done
  fi
  (( days += $3 ))
}
#-----------------------------------------------------------------------------
function leapYear {

# Checks if year is a leap year or not and adds the seconds of the year
# ARG1 Year

  if (( $1 % 400 ))
  then
    if (( $1 % 100 ))
    then
      if (( $1 % 4 ))
      then
        (( seconds += 31536000 )) ## non-leap year
      else
        (( seconds += 31622400 )) ## leap year
      fi
    else
      (( seconds += 31536000 )) ## non-leap year
    fi
  else
    (( seconds += 31622400 )) ## leap year
  fi
}
#-----------------------------------------------------------------------------

##############
#    MAIN
##############

# input
year=$1; mon=$2; day=$3; hou=$4; min=$5; sec=$6

# defaults
[[ $1 -eq '' ]] && year=1970
[[ $2 -eq '' ]] && mon=01
[[ $3 -eq '' ]] && day=01
[[ $4 -eq '' ]] && hou=00
[[ $5 -eq '' ]] && min=00
[[ $6 -eq '' ]] && sec=00

# calculate seconds
processYear=1970
seconds=0
days=-1
doy $year $mon $day
(( seconds = days * 86400 ))
(( seconds += ( hou * 3600) ))
(( seconds += ( min * 60) ))
(( seconds += sec ))

while [[ $processYear -lt year ]]
do
  leapYear $processYear
  (( processYear += 1 ))
done

print $seconds
#-----------------------------------------------------------------------------
#=END
