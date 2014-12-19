#/bin/ksh
#
#
# Calculate DOY from YYYYMMDD
# 
# 
# INPUT: Date in form of YYYY MM DD, e.g. 2008 06 20
#       
#
# OUTPUT:DOY
#
# AUTHOR M. Jerg, DWD
#

year=${1}
mons=${2}
day=${3}

#remove preceeding 0 from mons and day
mmons=`exec echo ${mons} |  awk '{print $1 + 0}'`
dday=`exec echo ${day} |  awk '{print $1 + 0}'`

doy=0

#is leap year? see below for test
ye1=$(( $year / 4 ))
ye2=$(( $ye1 * 4 ))		

#this is the counter for the months
ti=1

while [ ${ti} -lt ${mmons} ]
  do
  
#days in a months, cut correct month
  lengths="312831303130313130313031"
  cut2=$(( $ti * 2 ))
  cut1=$(( $cut2 - 1 ))
  numday=`echo $lengths | cut -c$cut1-$cut2`
  
#if leap year then numday=29
  if [ $ti -eq 2 ] && [ $year -eq $ye2 ] 
      then
      numday=29
  fi

  doy=$(( $doy + $numday ))
  ti=$(( $ti + 1 ))
done

doy=$(( $doy + ${dday} ))

echo $doy

#END