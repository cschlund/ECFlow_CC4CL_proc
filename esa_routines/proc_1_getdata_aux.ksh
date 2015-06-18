#!/usr/bin/ksh
#
# NAME
#       proc_1_get_data_aux.ksh
#
# PURPOSE
#       Extract auxiliary data from ECFS
#       gets one month of data
#
# HISTORY
#       2012-10-16 M.JERG DWD KU22
#       2014-04-08 MJ migration to cca/sf7
#       2015-01-13 C. Schlundt, take either NRT data or 
#                  if not available then take climatology file
#       2015-02-24 C. Schlundt: check data availability before ecp call
#           
# -------------------------------------------------------------------

data_on_scratch()
{
    NRT_TARGET=${1}
    CLI_TARGET=${2}

    printf "*** data_on_scratch() started\n"
    printf "    NRT PATH: $1\n"
    printf "    CLI PATH: $2\n"

    # availability flag
    aflag=-1

    if [ -d $NRT_TARGET ]; then 
        nfile=$(ls -A $NRT_TARGET/* | wc -l)
        lfile=$(ls -A $NRT_TARGET/*)

        if [ $nfile -gt 0 ]; then 
            printf "    NRT data already on scratch\n"
            printf "    $nfile file(s) in $NRT_TARGET\n"
            for i in $lfile; do 
                bas=$(basename $i)
                printf "    - $bas \n"
            done
            printf "\n"
            aflag=0
        fi
    fi

    if [ -d $CLI_TARGET ]; then 
        nfile=$(ls -A $CLI_TARGET/* |wc -l)
        lfile=$(ls -A $CLI_TARGET/*)

        if [ $nfile -gt 0 ]; then 
            printf "    CLIMATOLOGY data already on scratch\n"
            printf "    $nfile file(s) in $CLI_TARGET\n"
            for i in $lfile; do 
                bas=$(basename $i)
                printf "    - $bas \n"
            done
            printf "\n"
            aflag=0 
        fi
    fi

    if [ $aflag -ne 0 ]; then
        printf "    NO DATA on scratch yet!\n"
    fi
}


copy_file()
{
    SOURCE=${1}
    TARGET=${2}
    TYPE=${3}

    retcmk=-1
    retccp=-1
    retctar=-1

    echo "COPY_FILE: Make Copy " ${SOURCE} " TO " ${TARGET} 

    TARGETDIR=`dirname ${TARGET}` 
    mkdir -p ${TARGETDIR} 
    retcmk=${?} 

    if [ "${retcmk}" -eq 0  ]; then 

        echo "COPY_FILE: Made target directory: " ${TARGETDIR} 

        ecp -o ${SOURCE} ${TARGET} 
        retccp=${?} 

        if [ "${retccp}" -eq 0  ]; then 

            if [ "${TYPE}" -ne 3  ]; then 

                echo "COPY_FILE: Untarring " ${TARGET} 

                cd ${TARGETDIR} 
                tar xvf ${TARGET} 
                retctar=${?} 

                if [ "${retctar}" -eq 0 ]; then 
                    rm -f ${TARGET}
                else 
                    echo "ERROR: COPY_FILE:" ${TARGET} "untar FAILED" 
                fi 

            else 

                echo "COPY_FILE: Bunzipping " ${TARGET} 

                cd ${TARGETDIR} 
                ${free_path}/bunzip2 ${TARGET} 
                retctar=${?} 

                if [ "${retctar}" -ne 0 ]; then 
                    echo "ERROR: COPY_FILE:" ${TARGET} "untar FAILED" 
                fi 

            fi 

        else 
            echo "ERROR: COPY_FILE: Copying " ${SOURCE} " TO " ${TARGET} "FAILED!" 
        fi 

    else 
        echo "ERROR: COPY_FILE:"  `dirname ${TARGET}`  "NOT CREATED (FAILED)" 
    fi 

}


get_aux()
{
    SOURCE=${1}
    TARGET=${2}
    TYPE=${3}
    SOURCE_CLIMAT=${4}
    TARGET_CLIMAT=${5}
    YEAR=${6}

    printf "*** get_aux() started\n"
    #printf "    SOURCE: $SOURCE\n"
    #printf "    TARGET: $TARGET\n"
    #printf "    TYPE  : $TYPE\n"
    #printf "    SOURCE_CLIMAT: $SOURCE_CLIMAT\n"
    #printf "    TARGET_CLIMAT: $TARGET_CLIMAT\n"
    #printf "    YEAR: $YEAR\n"

    retcls=-1
    retcli=-1
    retlst=-1
    retrpl=-1

    # check if there is a directory and file for this day
    printf "    SOURCE: $SOURCE\n"
    check_source=$(els ${SOURCE})
    retcls=${?}
    
    if [ "${retcls}" -eq 0  ]; then 

        copy_file ${SOURCE} ${TARGET} ${TYPE}

    else

        printf "    SOURCE_CLIMAT: $SOURCE_CLIMAT\n"
        check_source_cli=$(els ${SOURCE_CLIMAT})
        retcli=${?}

        if [ "${retcli}" -eq 0 ]; then

            copy_file ${SOURCE_CLIMAT} ${TARGET_CLIMAT} ${TYPE}

            if [ "${TYPE}" -eq 2  ]; then 

                echo "REPLACE 1996 to $YEAR"
                targetdir=`dirname ${TARGET_CLIMAT}` 
                files=$(ls ${targetdir}/*1996*)
                retlst=${?}

                if [ "${retlst}" -eq 0 ]; then 

                    for file in $files; do
                        filebase=`basename $file`
                        newfilebase=${filebase/1996/$YEAR}
                        newfilename=$targetdir/$newfilebase
                        mv $file $newfilename
                        retrpl=${?}
                        
                        if [ "${retrpl}" -eq 0 ]; then
                            echo "GET_AUX: $newfilename successfully renamed"
                        else
                            echo "ERROR: GET_AUX: mv $file $newfilename FAILED"
                        fi

                    done

                else
                    echo "ERROR: GET_AUX: ls $targetdir/*AXXXX* FAILED"
                fi

            else

                echo "REPLACE XXXX to $YEAR"
                targetdir=`dirname ${TARGET_CLIMAT}` 
                files=$(ls ${targetdir}/*AXXXX*)
                retlst=${?}

                if [ "${retlst}" -eq 0 ]; then 

                    for file in $files; do
                        filebase=`basename $file`
                        newfilebase=${filebase/AXXXX/A$YEAR}
                        newfilename=$targetdir/$newfilebase
                        mv $file $newfilename
                        retrpl=${?}
                        
                        if [ "${retrpl}" -eq 0 ]; then
                            echo "GET_AUX: $newfilename successfully renamed"
                        else
                            echo "ERROR: GET_AUX: mv $file $newfilename FAILED"
                        fi

                    done

                else
                    echo "ERROR: GET_AUX: ls $targetdir/*AXXXX* FAILED"
                fi

            fi

        fi

    fi

    printf "*** get_aux() finished\n\n"
}

# -------------------------------------------------------------------
#
#          Main
#
# -------------------------------------------------------------------

set -v

# source path configfile 
. $1

# source proc 1 configfile
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

    CURRENT_DATE=${YEAR}${MONS}${DAYS}
    echo ""

    # subdir for climatology files in ecfs
    climat=climatology

    # this is where the stuff is in the ecfs 
    source_albedo=${toplevel_aux}/${albedo_ecfs}/${YEAR}/${MONS}/${DAYS}
    source_albedo_climatology=${toplevel_aux}/${albedo_ecfs}/${climat}/${MONS}/${DAYS}
    source_BRDF=${toplevel_aux}/${BRDF_ecfs}/${YEAR}/${MONS}/${DAYS}
    source_BRDF_climatology=${toplevel_aux}/${BRDF_ecfs}/${climat}/${MONS}/${DAYS}
    source_ice_snow=${toplevel_aux}/${ice_snow_ecfs}/${YEAR}/${MONS}/${DAYS}
    source_emissivity=${toplevel_aux}/${emissivity_ecfs}/${YEAR}/${MONS}/${DAYS}
    source_emissivity_climatology=${toplevel_aux}/${emissivity_ecfs}/${climat}

    # this is where the aux data goes on $TEMP
    target_albedo=${temp_aux}/${albedo_temp}/${YEAR}/${MONS}/${DAYS}
    target_albedo_climatology=${temp_aux}/${albedo_temp}/${YEAR}/${MONS}/${DAYS}
    target_BRDF=${temp_aux}/${brdf_temp}/${YEAR}/${MONS}/${DAYS}
    target_BRDF_climatology=${temp_aux}/${brdf_temp}/${YEAR}/${MONS}/${DAYS}
    target_ice_snow=${temp_aux}/${ice_snow_temp}/${YEAR}/${MONS}/${DAYS}
    target_emissivity=${temp_aux}/${emissivity_temp}/${YEAR}/${MONS}/${DAYS}
    target_emissivity_climatology=${temp_aux}/${emissivity_temp}/${YEAR}/${MONS}/${DAYS}


    # -- (1) get albedo --

    # required for unpacking source data on $TEMP
    TYPE=1

    # NRT data
    SOURCEPATH=${source_albedo}
    TARGETPATH=${target_albedo}
    SEARCHSTRING=${albedo_type}_${YEAR}${MONS}${DAYS}
    SOURCEFILE=${SOURCEPATH}/${SEARCHSTRING}${albedo_suffix}
    TARGETFILE=${TARGETPATH}/$(basename ${SOURCEFILE})

    # climatology data
    SOURCEPATH_CLIMAT=${source_albedo_climatology}
    TARGETPATH_CLIMAT=${target_albedo_climatology}
    SEARCHSTRING_CLIMAT=${albedo_type}_XXXX${MONS}${DAYS}
    SOURCEFILE_CLIMAT=${SOURCEPATH_CLIMAT}/${SEARCHSTRING_CLIMAT}${albedo_suffix}
    TARGETFILE_CLIMAT=${TARGETPATH_CLIMAT}/$(basename ${SOURCEFILE_CLIMAT})

    # availability check
    printf "\nData already on scratch for MODIS ALBEDO ${CURRENT_DATE}?\n"
    data_on_scratch ${target_albedo} ${target_albedo_climatology}

    if [ $aflag -ne 0 ]; then
        printf "\nGet MODIS ALBEDO data from ECFS for $CURRENT_DATE\n"
        get_aux ${SOURCEFILE} ${TARGETFILE} ${TYPE} ${SOURCEFILE_CLIMAT} ${TARGETFILE_CLIMAT} ${YEAR}
    fi


    # -- (2) get BRDF --

    # required for unpacking source data on $TEMP
    TYPE=1

    # NRT data
    SOURCEPATH=${source_BRDF}
    TARGETPATH=${target_BRDF}
    SEARCHSTRING=${BRDF_type}_${YEAR}${MONS}${DAYS}
    SOURCEFILE=${SOURCEPATH}/${SEARCHSTRING}${BRDF_suffix}
    TARGETFILE=${TARGETPATH}/$(basename ${SOURCEFILE})

    # climatology data
    SOURCEPATH_CLIMAT=${source_BRDF_climatology}
    TARGETPATH_CLIMAT=${target_BRDF_climatology}
    SEARCHSTRING_CLIMAT=${BRDF_type}_XXXX${MONS}${DAYS}
    SOURCEFILE_CLIMAT=${SOURCEPATH_CLIMAT}/${SEARCHSTRING_CLIMAT}${BRDF_suffix}
    TARGETFILE_CLIMAT=${TARGETPATH_CLIMAT}/$(basename ${SOURCEFILE_CLIMAT})

    # availability check
    printf "\nData already on scratch for MODIS BRDF ${CURRENT_DATE}?\n"
    data_on_scratch ${target_BRDF} ${target_BRDF_climatology}

    if [ $aflag -ne 0 ]; then
        printf "\nGet BRDF data from ECFS for $CURRENT_DATE\n"
        get_aux ${SOURCEFILE} ${TARGETFILE} ${TYPE} ${SOURCEFILE_CLIMAT} ${TARGETFILE_CLIMAT} ${YEAR}
    fi


    # -- (3) get emissivity --

    # required for unpacking source data on $TEMP
    TYPE=3

    #convert date to DOY for emissivity filename
    DOY=`exec ${ESA_ROUT}/date2doy.ksh ${YEAR} ${MONS} ${DAYS}`
    DDOY=${DOY} 
    if [ "${DOY}" -lt 10 ]; then
      DDOY=0${DOY}
    fi
    if [ "${DOY}" -lt 100 ]; then
      DDOY=0${DDOY}
    fi
    DOY=${DDOY}  

    # NRT data
    SOURCEPATH=${source_emissivity}
    TARGETPATH=${target_emissivity}
    SEARCHSTRING=${emissivity_type}${YEAR}${DOY}
    SOURCEFILE=${SOURCEPATH}/${SEARCHSTRING}${emissivity_suffix}
    TARGETFILE=${TARGETPATH}/$(basename ${SOURCEFILE})

    # climatology data
    SOURCEPATH_CLIMAT=${source_emissivity_climatology}
    TARGETPATH_CLIMAT=${target_emissivity_climatology}
    SEARCHSTRING_CLIMAT=${emissivity_type}XXXX${DOY}
    SOURCEFILE_CLIMAT=${SOURCEPATH_CLIMAT}/${SEARCHSTRING_CLIMAT}${emissivity_suffix}
    TARGETFILE_CLIMAT=${TARGETPATH_CLIMAT}/$(basename ${SOURCEFILE_CLIMAT})

    # availability check
    printf "\nData already on scratch for UWisc EMISSIVITY ${CURRENT_DATE}?\n"
    data_on_scratch ${target_emissivity} ${target_emissivity_climatology}

    if [ $aflag -ne 0 ]; then
        printf "\nGet EMISSIVITY data from ECFS for $CURRENT_DATE\n"
        get_aux ${SOURCEFILE} ${TARGETFILE} ${TYPE} ${SOURCEFILE_CLIMAT} ${TARGETFILE_CLIMAT} ${YEAR}
    fi


    # -- (4) get ice_snow --

    # required for unpacking source data on $TEMP
    TYPE=2

    # NRT data
    SOURCEPATH=${source_ice_snow}
    TARGETPATH=${target_ice_snow}
    SEARCHSTRING=${ice_snow_type}_${YEAR}${MONS}${DAYS}
    SOURCEFILE=${SOURCEPATH}/${SEARCHSTRING}${ice_snow_suffix}
    SOURCENAME=$(els $SOURCEFILE)
    if [ ${?} -ne 0 ]; then
        printf " --- FAILED: els $SOURCEFILE\n"
        SOURCENAME=$(basename $SOURCEFILE)
    else
        printf "SUCCESS: $SOURCENAME\n"
    fi
    TARGETFILE=${TARGETPATH}/${SOURCENAME} #`basename ${SOURCEFILE}`

    # temp. solution
    printf "\nNo NISE data available before 1995-05-04\n"
    MINUNIX=`${ESA_ROUT}/ymdhms2unix.ksh 1995 05 04`
    ACTUNIX=`${ESA_ROUT}/ymdhms2unix.ksh $YEAR $MONS $DAYS`

    if [ "${ACTUNIX}" -lt "${MINUNIX}" ]; then 
        TMPYEAR=1996
    fi

    # NRT before 19950504
    printf "\nThus: take TMPYEAR: $TMPYEAR (fake_climatology!) instead of $YEAR"
    source_ice_snow_fake=${toplevel_aux}/${ice_snow_ecfs}/${TMPYEAR}/${MONS}/${DAYS}
    target_ice_snow_fake=${temp_aux}/${ice_snow_temp}/${YEAR}/${MONS}/${DAYS}
    SOURCEPATH=${source_ice_snow_fake}
    TARGETPATH=${target_ice_snow_fake}
    SEARCHSTRING_CLIMAT=${ice_snow_type}_${TMPYEAR}${MONS}${DAYS}
    SOURCEFILE_CLIMAT=${SOURCEPATH}/${SEARCHSTRING_CLIMAT}${ice_snow_suffix}
    SOURCENAME_CLIMAT=$(els $SOURCEFILE_CLIMAT)
    if [ ${?} -ne 0 ]; then
        printf " --- FAILED: els $SOURCEFILE_CLIMAT\n"
        SOURCENAME_CLIMAT=$(basename $SOURCEFILE_CLIMAT)
    else
        printf "\nSUCCESS: $SOURCENAME_CLIMAT\n"
    fi
    TARGETFILE_CLIMAT=${TARGETPATH}/${SOURCENAME_CLIMAT} #`basename ${SOURCEFILE}`

    # availability check
    printf "\nData already on scratch for NISE ${CURRENT_DATE}?\n"
    data_on_scratch ${target_ice_snow} ${target_ice_snow_fake}

    if [ $aflag -ne 0 ]; then
        printf "\nGet NISE data from ECFS for $CURRENT_DATE\n"
        get_aux ${SOURCEFILE} ${TARGETFILE} ${TYPE} ${SOURCEFILE_CLIMAT} ${TARGETFILE_CLIMAT} ${YEAR}
    fi

    #echo "DAY=$DAYS"
    #if [ "$DAYS" -eq "02" ]; then exit; fi

    # go to next day
    (( unix_counter += 86400 ))

done
#----------------------------------------------------------------------------------------------

