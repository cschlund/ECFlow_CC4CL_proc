#!/bin/ksh
#
# proc_1_get_data_modis.ksh
#
#***
#
# ######################################################################################################
#
# NAME
#       proc_1_get_data_modis.ksh
#
# PURPOSE
#       Extract MODIS data from ECFS
#       gets one month of data
#
# USES
#
#
#
# HISTORY
#       2012-10-16  M.JERG DWD KU22
#           modified original version for AVHRR to use it for MODIS.
# 2014-04-08 MJ migration to cca/sf7
# 2014-04-11 MJ introduces some more statements in case of errors.
#
# ######################################################################################################
#-----------------------------------------------------------------------------
get_modis()
#
# get MODIS files from ECFS
#
# ARG1: year, e.g. 2007
# ARG2: month + day, e.g. 0824
#
#-----------------------------------------------------------------------------
#
{
    SOURCEFILE=${1}
    DATADIR=${2}
    cflag=${3}
    rflag=${4}
    rcut=${5}

    els ${SOURCEFILE}
    flag=${?}
    

    #just in case there are files, retrieve them:
    if [ "$flag" -eq 0  ] 
	then
        echo "GET_MODIS DATA:"
	echo ${SOURCEFILE}
	ecp ${SOURCEFILE} ${DATADIR}
	sret=${?}
    fi

    #was retrieval succesful? if not, return 1
    if [ "$sret" -ne 0  ]
	then
	echo "GET_MODIS FAILED: Not all files were retrieved from:"
	echo ${SOURCEFILE}
	echo "IN"
	echo ${DATADIR}
	return 1
    fi


    #now go into $DATADIR on $SCRATCH and unpack the tars
    #and throw them away once everything is untared.
    cd ${DATADIR}
    SOURCEFILE=`exec basename ${SOURCEFILE}`
    do_it=0
    RANDOM=10
    if [ "${cflag}" -eq 1 ]
	then
	if [ "${rflag}" -eq 1 ]
	    then
	    echo "RANDOM CHECKING REQUESTED"
	    
	    rn=${RANDOM}
	    rns=`expr ${rn}/32768*100 | bc -l`
	    rni=`exec echo $rns | cut -f 1 -d .`
	    rni1=`exec echo $rni | cut -c 1`
	    if [ "${rni1}" -eq 0 ]
		then
		rni=0
	    fi
	    
	    if [ "${rni}" -le rcut ]
		then
		echo "RANDOM NUMBER AND CUT" ${rni} ${rcut}
		do_it=1
	    fi
	    
	else
	    echo "STRICT CHECKING REQUESTED"
	    do_it=1
	fi

	if [ "$do_it" -eq 1 ]
	    then
	    
	    #checkname=`exec ls * | grep checksums`

	    checkname=`exec tar -tf ${SOURCEFILE} | grep checksums`
	    tar xf  ${SOURCEFILE}  && rm -f ${SOURCEFILE} 
	   
	    file=${checkname}
            # while loop
	    iline=0
	    ccounter=0
	    while read line
	      do
	      (( iline=$iline+1 )) # go to next line              
              # display line or do somthing on $line
	      
	      if [ "${iline}" -gt 4 ]
		  then
		  #echo $iline
		  #echo $line
		  cksumorg=`exec echo "$line" | awk '{print $1}'`
		  current_file=`exec echo "$line" | awk '{print $3}'`
		  cksumnew=`exec cksum ${current_file} | awk '{print $1}'`

		  front=`exec echo ${current_file} | cut -c1`
		  #extension=$(echo ${current_file}|awk -F\. '{print $2}')
		  if [ "${cksumorg}" -ne "${cksumnew}" ] && [ "${front}" = "M" ]
		      then
		    echo "Corrupt File:" $current_file ${cksumorg} ${cksumnew}
		    basefile=`exec basename ${current_file} .hdf`
		    mv $current_file $basefile.corrupt
		    (( ccounter=$ccounter+1 ))
		  fi
		  
	      fi
	    done <"$file"
	    
	    echo "FAILED: Number of corrupt files detected in " ${SOURCEFILE} ": " ${ccounter} 
	    	   
	fi


	

    else

	tar xf ${SOURCEFILE}  && rm -f ${SOURCEFILE} 

    fi
    

    
    



}
#-----------------------------------------------------------------------------
############################
#
#          Main
#
############################

set -xv

#source path configfile 
. $1

#source proc 1 configfile
. $2


#this was only for testing
#Get short product/platform specifier
#if [[ ${platform} = "aqua" ]]
#    then
#    splat=myd
#elif
#    [[ ${platform} = "terra" ]]
#    then
#    splat=mod
#fi

#Get short product/platform specifier
if [[ ${platform} = "MYD" ]]
    then
    splat=MYD
elif
    [[ ${platform} = "MOD" ]]
    then
    splat=MOD
fi

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
  DATADIR=${INPUTDIR}/MODIS/${platform}/${YEAR}/${MONS}/${DAYS}
  echo "CREATE AND WRITE DATA TO TARGETDIR:" $DATADIR
  mkdir -p $DATADIR

  #get doy from current date
  DOY=`exec ${ESA_ROUT}/date2doy.ksh ${YEAR} ${MONS} ${DAYS}`
  echo ${YEAR} ${MONS} ${DAYS} "IS DOY " $DOY "OF " ${YEAR}

  #Build now path to MODIS files of that given doy
  #SOURCEL1B=${modis_top}/${platform}/${YEAR}${DOY}/${splat}02/${splat}02.tar
  #SOURCEGEO=${modis_top}/${platform}/${YEAR}${DOY}/${splat}03/${splat}03.tar
  SOURCEL1B=${modis_top}/${platform}/${YEAR}${MONS}/${splat}021km_${YEAR}_${MONS}_${DAYS}.tar
  SOURCEGEO=${modis_top}/${platform}/${YEAR}${MONS}/${splat}03_${YEAR}_${MONS}_${DAYS}.tar

  #Get those files from ECFS
  get_modis ${SOURCEL1B} ${DATADIR} ${cflag} ${rflag} ${rcut}
  retcl1b=${?}

  get_modis ${SOURCEGEO} ${DATADIR} ${cflag} ${rflag} ${rcut}
  retcgeo=${?}

    retc=1

  if [ "${retcl1b}" -eq 0 ] && [ "${retcgeo}" -eq 0 ]
      then
      retc=0

      echo "SUCCESS: All files  retrieved for " ${splat} "on " ${YEAR}${MONS}${DAYS} "."

  else

      echo "ERROR: GET_MODIS FAILED: Not all files were retrieved for " ${splat} "on " ${YEAR}${MONS}{DAYS} "." ${retcl1b} ${retcgeo}

  fi

  (( unix_counter += 86400 )) # go to next day

done
#----------------------------------------------------------------------------------------------

