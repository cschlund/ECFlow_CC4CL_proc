#!/usr/bin/ksh
#
# proc_1_get_data_aux.ksh
#
#***
#
# ######################################################################################################
#
# NAME
#       proc_1_get_data_aux.ksh
#
# PURPOSE
#       Extract auxiliary data from ECFS
#       gets one month of data
#
# USES
#
#
#
# HISTORY
#       2012-10-16  M.JERG DWD KU22
# 2014-04-08 MJ migration to cca/sf7
#           
#
# ######################################################################################################
get_aux()
#
# put MODIS files into ECFS
#
#
#-----------------------------------------------------------------------------
#
{
    SOURCE=${1}
    TARGET=${2}
    TYPE=${3}

    retcls=-1
    retcmk=-1
    retccp=-1
    retctar=-1

    #check if there is a directory and file for this day
    els ${SOURCE}
    retcls=${?}
    
    if [ "${retcls}" -eq 0  ]
	then
	echo "GET_AUX: Make Copy " ${SOURCE} " TO " ${TARGET}
	TARGETDIR=`dirname ${TARGET}`
	mkdir -p ${TARGETDIR}
	retcmk=${?}
	if [ "${retcmk}" -eq 0  ]
	    then
	    echo "GET_AUX: Made target directory: " ${TARGETDIR}
	    ecp -o ${SOURCE} ${TARGET}
	    retccp=${?}
	    
	    if [ "${retccp}" -eq 0  ]
		then
		if [ "${TYPE}" -ne 3  ]
		then
		    echo "GET_AUX: Untarring " ${TARGET}
		    cd ${TARGETDIR}
		    tar xvf ${TARGET}
		    retctar=${?}

		    if [ "${retctar}" -eq 0 ] 
			then
			rm -f ${TARGET}    

		    else

		    echo "ERROR: GET_AUX:" ${TARGET} "untar FAILED"

		    fi

		 else
		    echo "GET_AUX: Bunzipping " ${TARGET}
		    cd ${TARGETDIR}
		    ${free_path}/bunzip2 ${TARGET}
		    retctar=${?}

		    if [ "${retctar}" -ne 0 ] 
			then
		    echo "ERROR: GET_AUX:" ${TARGET} "untar FAILED"
		    fi

		fi

	    
	    else

	    echo "ERROR: GET_AUX: Copying " ${SOURCE} " TO " ${TARGET} "FAILED!"

	    fi

	else

	    echo "ERROR: GET_AUX:"  `dirname ${TARGET}`  "NOT CREATED (FAILED)"

	fi

    fi



}
#-----------------------------------------------------------------------------
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

  #this is where the stuff is in the ecfs 
  source_albedo=${toplevel_aux}/${albedo_ecfs}/${YEAR}/${MONS}/${DAYS}
  source_BRDF=${toplevel_aux}/${BRDF_ecfs}/${YEAR}/${MONS}/${DAYS}
  source_ice_snow=${toplevel_aux}/${ice_snow_ecfs}/${YEAR}/${MONS}/${DAYS}
  source_emissivity=${toplevel_aux}/${emissivity_ecfs}/${YEAR}/${MONS}/${DAYS}

  #this is where the aux data goes on $TEMP
  target_albedo=${temp_aux}/${albedo_temp}/${YEAR}/${MONS}/${DAYS}
  target_BRDF=${temp_aux}/${brdf_temp}/${YEAR}/${MONS}/${DAYS}
  target_ice_snow=${temp_aux}/${ice_snow_temp}/${YEAR}/${MONS}/${DAYS}
  target_emissivity=${temp_aux}/${emissivity_temp}/${YEAR}/${MONS}/${DAYS}

  #get albedo
  SOURCEPATH=${source_albedo}
  TARGETPATH=${target_albedo}
  SEARCHSTRING=${albedo_type}_${YEAR}${MONS}${DAYS}
  SOURCEFILE=${SOURCEPATH}/${SEARCHSTRING}${albedo_suffix}
  TARGETFILE=${TARGETPATH}/`basename ${SOURCEFILE}`
  TYPE=1
  get_aux ${SOURCEFILE} ${TARGETFILE} ${TYPE}

  #get BRDF
  SOURCEPATH=${source_BRDF}
  TARGETPATH=${target_BRDF}
  SEARCHSTRING=${BRDF_type}_${YEAR}${MONS}${DAYS}
  SOURCEFILE=${SOURCEPATH}/${SEARCHSTRING}${BRDF_suffix}
  TARGETFILE=${TARGETPATH}/`basename ${SOURCEFILE}`
  TYPE=1
  get_aux ${SOURCEFILE} ${TARGETFILE} ${TYPE}

  #get ice_snow
  SOURCEPATH=${source_ice_snow}
  TARGETPATH=${target_ice_snow}
  SEARCHSTRING=${ice_snow_type}_${YEAR}${MONS}${DAYS}
  SOURCEFILE=${SOURCEPATH}/${SEARCHSTRING}${ice_snow_suffix}
  SOURCENAME=`els $SOURCEFILE`
  TARGETFILE=${TARGETPATH}/${SOURCENAME} #`basename ${SOURCEFILE}`
  TYPE=2
  get_aux ${SOURCEFILE} ${TARGETFILE} ${TYPE}

  #get emissivity
  SOURCEPATH=${source_emissivity}
  TARGETPATH=${target_emissivity}

  #convert date to DOY for emissivity filename
  DOY=`exec ${ESA_ROUT}/date2doy.ksh ${YEAR} ${MONS} ${DAYS}`
  DDOY=${DOY} 
  if [ "${DOY}" -lt 10 ]
    then
    DDOY=0${DOY}
  fi
  if [ "${DOY}" -lt 100 ]
    then
    DDOY=0${DDOY}
  fi
  DOY=${DDOY}  

  SEARCHSTRING=${emissivity_type}${YEAR}${DOY}
  SOURCEFILE=${SOURCEPATH}/${SEARCHSTRING}${emissivity_suffix}
  TARGETFILE=${TARGETPATH}/`basename ${SOURCEFILE}`
  TYPE=3
  get_aux ${SOURCEFILE} ${TARGETFILE} ${TYPE}


  (( unix_counter += 86400 )) # go to next day

done
#----------------------------------------------------------------------------------------------

