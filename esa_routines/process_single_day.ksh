#!/bin/ksh
#
# NAME
#       process_single_day.ksh
#
# PURPOSE
#       Process one day for ESA CCI clouds   
#
# HISTORY
#       2012-05-15  A.Kniffka DWD KU22, created
#       2012-07-03 onward  M. Jerg DWD KU22 
#       extended for ESA CLOUD CCI ECV PRODUCTION:
#       - construction of input file lists
#       - logging
#       - driver file construction and passing
#       - conncting the chain components
#       - I/O control
#       - MODIS/AVHRR implementation
#       - flexible paths
#       - OMP ENVIRONMENT VARIABLES
#       2014-04-15 MJ migration to cca/sf7, Stage I
#

# C. Schlundt, 12.06.2015
# function for grep path_and_file_string from 
# returncode ofpython script pick_aux_dir.py
grep_wanted()
{
    STRING=$1
    PICK_AUX_RETURN=PICK_AUX_RETURN:
    LEN_RETCODE=${#PICK_AUX_RETURN}
    split_string=$(echo ${STRING} | tr " " "\n")
    for str in ${split_string}; do 
        if [[ ${str} == *$PICK_AUX_RETURN* ]]; then 
            len=${#str}
            ret=`exec echo ${str} | cut -c $((LEN_RETCODE + 1))-$len` 
            echo "${ret}"
            break
        fi  
    done 
}

set -x

# -- source config path files
config_file_paths=${1}
. ${config_file_paths}
echo

# -- source config attributes file
config_file_attributes=${2}
. ${config_file_attributes}
echo

# -- daily configfile for this task, e. g.
config_file_daily=${3}
. ${3} 
echo

# -- daily log file number
log_file_daily=${4}
itask=${4}
echo


# -- format month and day string
MONTHS=$(printf %02d $MONTH)
DAYS=$(printf %02d $DAY)


rm -f ${daily_log}
touch ${daily_log}

if [ ${?} -ne 0 ]; then 
    echo "#------------------------------------------#" >> ${daily_log}
    echo "#------------------------------------------#" >> ${daily_log}
    echo `exec date +%Y/%m/%d:%H:%M:%S` "PROCESSING OF DATE" ${YEAR}${MONTHS}${DAYS} "OF" ${INSTRUMENT} "ON" ${PLATFORM} "WITH ID" ${ID} "FAILED TO START" >> ${daily_log}
    echo "#------------------------------------------#" >> ${daily_log}
    echo "#------------------------------------------#" >> ${daily_log}
    exit
else
    echo "#------------------------------------------#" >> ${daily_log}
    echo "#------------------------------------------#" >> ${daily_log}
    echo `exec date +%Y/%m/%d:%H:%M:%S` "PROCESSING OF DATE" ${YEAR}${MONTHS}${DAYS} "OF" ${INSTRUMENT} "ON" ${PLATFORM} "WITH ID" ${ID} "STARTED SUCCESSFULLY ON" ${HOST} "AND" ${itask} >> ${daily_log}
    echo "#------------------------------------------#" >> ${daily_log}
    echo "#------------------------------------------#" >> ${daily_log}
fi

echo `exec date +%Y/%m/%d:%H:%M:%S` "SET PLATFORMS" >> ${daily_log}


# -- now fill them with the paths to the files to be processed
if [[ ${INSTRUMENT} = "AVHRR" ]]; then
    
    l1_dirbase=${INPUTDIR}/${INSTRUMENT}/${PLATFORM}
    l1_dirname=${l1_dirbase}/${YEAR}/${MONTHS}/${DAYS}/${YEAR}${MONTHS}${DAYS}
    l1_filename=$(ls ${l1_dirname}/*.h5 | head -1)
    l1_filebase=`exec basename ${l1_filename} .h5`

    SPLATFORM=${PLATFORM}

    if [[ ${PLATFORM} = "all" ]]; then  
	
        if [[ ${l1_filebase} == ECC_GAC* ]]; then 
            # -- new file nomenclature (pygac)
	        searchl1b=*avhrr*h5
	        searchgeo=*sunsatangles*h5
        else
            # -- old file nomenclature
	        searchl1b=*_avhrr.h5
	        searchgeo=*_sunsatangles.h5
        fi

    else

        if [[ ${l1_filebase} == ECC_GAC* ]]; then 
            # -- new file nomenclature (pygac)
	        searchl1b=*avhrr*${PLATFORM}*h5
	        searchgeo=*sunsatangles*${PLATFORM}*h5
        else
            # -- old file nomenclature
	        searchl1b=${PLATFORM}*_avhrr.h5
	        searchgeo=${PLATFORM}*_sunsatangles.h5
        fi
	
    fi

elif [[ ${INSTRUMENT} = "MODIS" ]]; then
  
    if [[ ${PLATFORM} = "all" ]]; then  
	
	    searchl1b=M*D021KM.*.hdf
	    searchgeo=M*D03.*.hdf

    elif [[ ${PLATFORM} = "AQUA" ]]; then

        SPLATFORM="MYD"

        searchl1b=${SPLATFORM}021KM.*.hdf
        searchgeo=${SPLATFORM}03.*.hdf

    elif [[ ${PLATFORM} = "TERRA" ]];then

	    SPLATFORM="MOD"

	    searchl1b=${SPLATFORM}021KM.*.hdf
	    searchgeo=${SPLATFORM}03.*.hdf

    fi
    
fi


echo `exec date +%Y/%m/%d:%H:%M:%S` "MAKE DIRS/FILES" >> ${daily_log}

inputdir_instr=${INPUTDIR}/${INSTRUMENT}

# -- make output directory for the day
mkdir -p ${DAILY_OUTP}
if [ ${?} -ne 0 ]; then
    echo "CREATION OF" ${DAILY_OUTP} "FAILED" >> ${daily_log}
    exit
fi


# -- create checkfile:
checkfile=${DAILY_OUTP}/check_${YEAR}${MONTHS}${DAYS}_${INSTRUMENT}_${PLATFORM}_${ID}.dat

rm -f ${checkfile}
touch ${checkfile}

if [ ${?} -ne 0 ]; then
    echo "CREATION OF" ${checkfile} "FAILED" >> ${daily_log}
    exit
else 
    echo `exec date +%Y/%m/%d:%H:%M:%S` ${YEAR}${MONTHS}${DAYS} "OF" ${INSTRUMENT} "ON" ${PLATFORM} "WITH ID" ${ID} 'Running on' ${HOST} 'and'  ${itask} >> ${checkfile} 
fi


# -- create those two files first:
l1b_file=${DAILY_OUTP}/l1b_${YEAR}${MONTHS}${DAYS}_${INSTRUMENT}_${PLATFORM}_${ID}.dat
geo_file=${DAILY_OUTP}/geo_${YEAR}${MONTHS}${DAYS}_${INSTRUMENT}_${PLATFORM}_${ID}.dat

rm -f ${l1b_file}
rm -f ${geo_file}

touch ${l1b_file}
if [ ${?} -ne 0 ]; then
    echo "CREATION OF" ${l1b_file} "FAILED" >> ${daily_log}
    exit
fi

touch ${geo_file}
if [ ${?} -ne 0 ]; then
    echo "CREATION OF"  ${geo_file} "FAILED" >> ${daily_log}
    exit
fi


# -- reset counters
il1b=0
igeo=0


# --  Build the directory where the input data is staged by proc1
if [[ ${INSTRUMENT} = "AVHRR" ]]; then

    inputdir_instr_date=${inputdir_instr}/${PLATFORM}/${YEAR}/${MONTHS}/${DAYS}/${YEAR}${MONTHS}${DAYS}
    
elif [[ ${INSTRUMENT} = "MODIS" ]]; then
  
    inputdir_instr_date=${inputdir_instr}/${SPLATFORM}/${YEAR}/${MONTHS}/${DAYS}
    
fi


echo `exec date +%Y/%m/%d:%H:%M:%S` "MAKE FILE LISTS" >> ${daily_log}

searchstring=${inputdir_instr_date}/${searchl1b}

nl1b_check=`ls $searchstring | wc -l`

if [ nl1b_check -eq 0 ]; then
    echo "NO DATA TO PROCESS AVAILABLE! EXITING, PROCESSING FAILED FOR" ${YEAR}${MONTHS}${DAYS} "OF" ${INSTRUMENT} "ON" ${PLATFORM} "WITH ID" ${ID} 'Running on' ${HOST} >> ${daily_log}
    echo "nl1b == 0" >> ${daily_log}
    exit
fi


for f in $searchstring; do

    echo "Adding $f"

    echo '"'$f'"' >> ${l1b_file}
    
    l1b_list[$il1b]=$f

    ((il1b=il1b+1))

done


searchstring=${inputdir_instr_date}/${searchgeo}

ngeo_check=`ls $searchstring | wc -l`

# -- check if numbers are equal and greater zero:
if [ nl1b_check -ne ngeo_check ]; then   
    echo "NUMBERS OF FILES TO PROCESS DO NOT MATCH! PROCESSING FAILED...EXITING" >> ${daily_log}
    echo "nl1b="$nl1b_check"!=ngeo="$ngeo_check >> ${daily_log}
    exit
fi


echo `exec date +%Y/%m/%d:%H:%M:%S` "A TOTAL OF"  $nl1b_check " FILES WILL BE PROCESSED" >> ${daily_log}


for f in $searchstring;do
	
    echo "Adding $f"
    
    echo '"'$f'"' >> ${geo_file}

    geo_list[$igeo]=$f

    ((igeo=igeo+1))

done


nl1b=${#l1b_list[*]}
ngeo=${#geo_list[*]}

# -- now loop over the files and process them step by step
ifile=0
lpick=0

path_to_emiss_atlas=${perm_aux}/emis_atlas
path_to_ice=${temp_aux}/${ice_snow_temp}
path_to_albedo=${temp_aux}/${albedo_temp}
path_to_brdf=${temp_aux}/${brdf_temp}
path_to_emissivity=${temp_aux}/${emissivity_temp}


# -- get days (directories) for ice_snow, albedo, BRDF (emissivity to be implemented)
echo `exec date +%Y/%m/%d:%H:%M:%S` "PICK AUX FILES" >> ${daily_log}    


# -- modis albedo
echo `exec date +%Y/%m/%d:%H:%M:%S` "PICK ALBEDO" >> ${daily_log}    
aux_input_dir=${path_to_albedo}
suffix=hdf
type=alb
pick_logsoutput=$(python $pick_aux_datafile \
    --inpdir $aux_input_dir --suffix $suffix \
    --year $YEAR --month $MONTHS --day $DAYS)
echo $pick_logsoutput
path_and_file_to_albedo=$(grep_wanted "$pick_logsoutput")


# -- modis brdf
echo `exec date +%Y/%m/%d:%H:%M:%S` "PICK BRDF" >> ${daily_log}    
aux_input_dir=${path_to_brdf}
suffix=hdf
type=brdf
pick_logsoutput=$(python $pick_aux_datafile \
    --inpdir $aux_input_dir --suffix $suffix \
    --year $YEAR --month $MONTHS --day $DAYS)
echo $pick_logsoutput
path_and_file_to_brdf=$(grep_wanted "$pick_logsoutput")

# -- ice_snow
echo `exec date +%Y/%m/%d:%H:%M:%S` "PICK SNOW" >> ${daily_log}    
aux_input_dir=${path_to_ice}
suffix=HDFEOS
type=is
pick_logsoutput=$(python $pick_aux_datafile \
    --inpdir $aux_input_dir --suffix $suffix \
    --year $YEAR --month $MONTHS --day $DAYS)
echo $pick_logsoutput
path_and_file_to_ice=$(grep_wanted "$pick_logsoutput")


# -- emissivity
echo `exec date +%Y/%m/%d:%H:%M:%S` "PICK EMIS" >> ${daily_log}    
aux_input_dir=${path_to_emissivity}
suffix=nc
type=em
pick_logsoutput=$(python $pick_aux_datafile \
    --inpdir $aux_input_dir --suffix $suffix \
    --year $YEAR --month $MONTHS --day $DAYS)
echo $pick_logsoutput
path_and_file_to_emissivity=$(grep_wanted "$pick_logsoutput")


lpick=1

echo `exec date +%Y/%m/%d:%H:%M:%S` "START LOOP OVER FILES" >> ${daily_log}

while [ $ifile -lt $nl1b ]; do 

    echo `exec date +%Y/%m/%d:%H:%M:%S` "PROCESSING OF ITEM" ${l1b_list[$ifile]} "STARTED" >> ${daily_log} 
    echo "FILE" $((${ifile}+1)) "OF" ${nl1b} "IS IN WORK" >> ${daily_log}
          

    # --------------------------------------------------------------------- #
    #                                                                       #
    #       PREPARATIONS: SETTING SOME GENERAL STUFF                        #
    #                                                                       #
    # --------------------------------------------------------------------- #

    uuid_tag=`exec $uuid_path`
    exec_time_pre_d=`exec date +%Y%m%d`
    exec_time_pre_h=`exec date +%H%M%S`
    exec_time_pre=${exec_time_pre_d}T${exec_time_pre_h}Z
    sensor=${INSTRUMENT}
    path_to_l1b=${l1b_list[$ifile]}
    path_to_geo=${geo_list[$ifile]}
    path_to_USGS=${USGS_file}
    path_to_ecmwf=${INPUTDIR}/ERAinterim/${YEAR}/${MONTHS}/${DAYS}
    path_to_coeffs=${perm_aux}/coeffs


    echo `exec date +%Y/%m/%d:%H:%M:%S` "MAKE OUTPUT DIRS" >> ${daily_log}

    # -- make output directory for that given orbit/granule
    if [[ ${INSTRUMENT} = "AVHRR" ]]; then 

        # -- setting hour and minute from AVHRR filename 
        l1b_file=`exec basename ${l1b_list[ifile]} .h5` 

        if [[ ${l1_filebase} == ECC_GAC* ]]; then 

            # -- new avhrr file nomenclature
            #ECC_GAC_avhrr_noaa18_99999_20100101T0000406Z_20100101T0141446Z.h5
            fsplit=$(echo ${l1b_file} | tr "_" "\n")
            for x in ${fsplit}; do 
                if [[ ${x} == *T*Z ]]; then 
                    HOUR=`exec echo ${x} | cut -c 10-11` 
                    MINUTE=`exec echo ${x} | cut -c 12-13` 
                    break 
                fi  
            done 

        else

            # -- old avhrr file nomenclature
            #noaa18_20080101_2228_99999_satproj_11018_12302_avhrr.h5
	        HOUR=`exec echo ${l1b_file} | rev | cut -c 35-36 | rev`
	        MINUTE=`exec echo ${l1b_file} | rev | cut -c 33-34 | rev`

        fi


    elif [[ ${INSTRUMENT} = "MODIS" ]]; then 

        # -- setting hour and minute from MODIS filename
        l1b_file=`exec basename ${l1b_list[ifile]} .hdf` 
	    HOUR=`exec echo ${l1b_file} | cut -f 3-3 -d . | cut -c 1-2`
	    MINUTE=`exec echo ${l1b_file} | cut -f 3-3 -d . | cut -c 3-4` 

    fi

    l2_outp=${DAILY_OUTP}/${l1b_file}

    mkdir -p ${l2_outp}
    if [ ${?} -ne 0 ]; then 
        echo "CREATION OF" ${l2_outp} "FAILED. GOING TO NEXT ITEM" >> ${daily_log} 
        echo `exec date +%Y/%m/%d:%H:%M:%S` ${l1b_list[$ifile]} ' _F_' >> ${checkfile} 
        continue
    fi
    

    echo `exec date +%Y/%m/%d:%H:%M:%S` "PICK ECMWF FILE" >> ${daily_log}

    # -- pick ecmwf file
    aux_input_dir=${path_to_ecmwf}
    suffix=nc #grb
    pick_logsoutput=$(python $pick_aux_datafile \
        --inpdir $aux_input_dir --suffix $suffix \
        --year $YEAR --month $MONTHS --day $DAYS \
        --hour $HOUR --minute $MINUTE)
    echo $pick_logsoutput
    path_to_ecmwf=$(grep_wanted "$pick_logsoutput")


    # --------------------------------------------------------------------- #
    #                                                                       #
    #       PRE-PROCESSING                                                  #
    #                                                                       #
    # --------------------------------------------------------------------- #

    # -- make preproc output directory
    l2_outp_pre=${l2_outp}/pre_proc

    mkdir -p ${l2_outp_pre}
    if [ ${?} -ne 0 ]; then 
        echo "CREATION OF PREPROCDIR " ${l2_outp_pre} "FAILED. GOING TO NEXT ITEM" >> ${daily_log} 
        echo `exec date +%Y/%m/%d:%H:%M:%S` ${l1b_list[$ifile]} ' _F_' >> ${checkfile} 
        ((ifile=$ifile+1)) 
        continue
    fi 


    # -- write information in config file for preprocessing
    preproc_driver=${l2_outp}/preproc_driver_${l1b_file}.dat

    rm -f ${preproc_driver}
    touch ${preproc_driver}

    . ${ESA_ROUT}/write_preproc_file.ksh

    if [ ${?} -ne 0 ]; then 
        echo "WRITING OF PREPROCDRIVER" ${preproc_driver} "FAILED. GOING TO NEXT ITEM" >> ${daily_log} 
        echo `exec date +%Y/%m/%d:%H:%M:%S` ${l1b_list[$ifile]} ' _F_' >> ${checkfile} 
        ((ifile=$ifile+1)) 
        continue
    fi     
      
    
    echo `exec date +%Y/%m/%d:%H:%M:%S` "STARTING  PREPROCESSING" ${preproc_driver} "ON" ${OMP_NUM_THREADS} "THREADS" >> ${daily_log}

    if [ ${?} -ne 0 ]; then 
        echo "RUNNING OF PREPROCESSING" ${preproc_driver} "FAILED. GOING TO NEXT ITEM" >> ${daily_log} 
        echo `exec date +%Y/%m/%d:%H:%M:%S` ${l1b_list[$ifile]} ' _F_' >> ${checkfile} 
        ((ifile=$ifile+1)) 
        continue 
    else 
        echo `exec date +%Y/%m/%d:%H:%M:%S` "RUNNING OF PREPROCESSING" ${preproc_driver} "SUCCESSFUL" >> ${daily_log}
    fi     



    # --------------------------------------------------------------------- #
    #                                                                       #
    #       MAIN-PROCESSING                                                 #
    #                                                                       #
    # --------------------------------------------------------------------- #

    # -- set stuff for main processing (ORAC)
    # -- set back again on maximum threads from LL

    echo `exec date +%Y/%m/%d:%H:%M:%S` "STARTING  PROCESSING" ${preproc_driver} "ON" ${OMP_NUM_THREADS} "THREADS" >> ${daily_log}
      
    # -- make main proc output directory      
    l2_outp_main=${l2_outp}/main

    mkdir -p ${l2_outp_main}
    if [ ${?} -ne 0 ]; then 
        echo "CREATION OF PROCDIR " ${l2_outp_main} "FAILED. GOING TO NEXT ITEM" >> ${daily_log} 
        echo `exec date +%Y/%m/%d:%H:%M:%S` ${l1b_list[$ifile]} ' _F_' >> ${checkfile} 
        ((ifile=$ifile+1)) 
        continue
    fi  
    
    uuid_tag=`exec $uuid_path`
    exec_time_main=`exec date +%Y%m%d:%H%M%S`
    path_to_sads=${perm_aux}/sad_dir

    # -- determine here platform part of tag
    # -- if AVHRR there is no platform part
    if [[ ${INSTRUMENT} = "AVHRR" ]]; then 

        typeset -u UPLATFORM=${PLATFORM} 
        CPLATFORM=${UPLATFORM}

	    sensor_platform=${INSTRUMENT}-${CPLATFORM}
	    sensor_version=${sensor_version_avhrr}

    elif [[ ${INSTRUMENT} = "MODIS" ]]; then 

        if [[ ${PLATFORM} = "all" ]]; then 

            if [[ ${l1b_file} = *MOD* ]]; then 
                CPLATFORM="TERRA" 
            elif [[ ${l1b_file} = *MYD* ]]; then 
                CPLATFORM="AQUA" 
            fi 

        else 

            CPLATFORM=${PLATFORM} 

        fi 

        sensor_platform=${INSTRUMENT}-${CPLATFORM} 
        sensor_version=${sensor_version_modis} 

    fi
      

    # -- set preprocessing basename
    preproc_base=${project}_${processing_inst}_${INSTRUMENT}_${l2processor}V${l2proc_version}_${PLATFORM}_${exec_time_pre}_${YEAR}${MONTHS}${DAYS}${HOUR}${MINUTE}_${file_version}


    # -- process first WATer phase
    phase=WAT
    wat_out_path=${l2_outp_main}/${preproc_base}${phase}


    # -- write information in config file for processing
    mainproc_driver=${l2_outp}/mainproc_driver_${l1b_file}_${phase}.dat

    rm -f ${mainproc_driver}
    touch ${mainproc_driver}
    . ${ESA_ROUT}/write_orac_file.ksh

    if [ ${?} -ne 0 ]; then 
        echo "WRITING OF PROCDRIVER FOR" ${mainproc_driver} "FAILED. GOING TO NEXT ITEM" >> ${daily_log} 
        echo `exec date +%Y/%m/%d:%H:%M:%S` ${l1b_list[$ifile]} ' _F_' >> ${checkfile} 
        ((ifile=$ifile+1)) 
        continue
    fi     


    # -- run main processing, pass path and filename of ORAC driver file to it.
    if [ ${?} -ne 0 ]; then 
        echo "RUNNING OF PROCESSING" ${mainproc_driver} "FAILED. GOING TO NEXT ITEM" >> ${daily_log} 
        echo `exec date +%Y/%m/%d:%H:%M:%S` ${l1b_list[$ifile]} ' _F_' >> ${checkfile} 
        ((ifile=$ifile+1)) 
        continue 
    else 
        echo `exec date +%Y/%m/%d:%H:%M:%S` "RUNNING OF PROCESSING" ${mainproc_driver} "SUCCESSFUL" >> ${daily_log}
    fi     
      
      
    # -- process then ICE phase
    phase=ICE
    ice_out_path=${l2_outp_main}/${preproc_base}${phase}
    
    # -- write information in config file for processing
    mainproc_driver=${l2_outp}/mainproc_driver_${l1b_file}_${phase}.dat

    rm -f ${mainproc_driver}
    touch ${mainproc_driver}
    . ${ESA_ROUT}/write_orac_file.ksh

    if [ ${?} -ne 0 ]; then 
        echo "WRITING OF PROCDRIVER FOR" ${mainproc_driver} "FAILED. GOING TO NEXT ITEM" >> ${daily_log} 
        echo `exec date +%Y/%m/%d:%H:%M:%S` ${l1b_list[$ifile]} ' _F_' >> ${checkfile} 
        ((ifile=$ifile+1)) 
        continue
    fi


    # -- run main processing, pass path and filename of ORAC driver file to it.
    if [ ${?} -ne 0 ]; then 
        echo "RUNNING OF PROCESSING" ${mainproc_driver} "FAILED. GOING TO NEXT ITEM" >> ${daily_log} 
        echo `exec date +%Y/%m/%d:%H:%M:%S` ${l1b_list[$ifile]} ' _F_' >> ${checkfile} 
        ((ifile=$ifile+1)) 
        continue
    else 
        echo `exec date +%Y/%m/%d:%H:%M:%S` "RUNNING OF PROCESSING" ${mainproc_driver} "SUCCESSFUL" >> ${daily_log}
    fi     
      


    # --------------------------------------------------------------------- #
    #                                                                       #
    #       POST-PROCESSING                                                 #
    #                                                                       #
    # --------------------------------------------------------------------- #

    # -- write information in config file for post-processing
    postproc_driver=${l2_outp}/postproc_driver_${l1b_file}.dat

    rm -f ${postproc_driver}
    touch ${postproc_driver}

    # -- make post proc output directory
    # -- where combined WAT/ICE result sits:       
    l2_outp_post=${l2_outp}/post

    mkdir -p ${l2_outp_post} 
    if [ ${?} -ne 0 ]; then 
        echo "CREATION OF POSTPROCDIR " ${l2_outp_post} "FAILED. GOING TO NEXT ITEM" >> ${daily_log} 
        echo `exec date +%Y/%m/%d:%H:%M:%S` ${l1b_list[$ifile]} ' _F_' >> ${checkfile} 
        ((ifile=$ifile+1)) 
        continue
    fi  

    uuid_tag_primary=`exec $uuid_path`
    uuid_tag_secondary=`exec $uuid_path`
    exec_time_post=`exec date +%Y%m%d:%H%M%S`
    source=${sensor}_${CPLATFORM}_${sensor_version}
    file_name=${l1b_file}.nc
    cstandard_name_voc=`echo "'"${standard_name_voc}"'"`      
    cprod_name=`echo "'"${prod_name}"'"`      
    chistory=`echo "'"${history}"'"`      
    ccomment=`echo "'"${comment}"'"`      
    clicense=`echo "'"${license}"'"`      
    csummary=`echo "'"${summary}"'"`      
    ckeywords=`echo "'"${keywords}"'"`
    cprocessing_inst=`echo "'"${processing_inst}"'"`      
    cproject=`echo "'"${project}"'"`      


    # -- name of combined result
    comb_out_path=${l2_outp_post}/${l1b_file}
    . ${ESA_ROUT}/write_post_file.ksh

    if [ ${?} -ne 0 ]; then 
        echo "WRITING OF POSTPROCDRIVER FOR" ${postproc_driver} "FAILED. GOING TO NEXT ITEM" >> ${daily_log} 
        echo `exec date +%Y/%m/%d:%H:%M:%S` ${l1b_list[$ifile]} ' _F_' >> ${checkfile} 
        ((ifile=$ifile+1)) 
        continue
    fi


    # -- run postprocessing
    if [ ${?} -ne 0 ]; then 

        echo "RUNNING OF POSTPROCESSING" ${postproc_driver} "FAILED. GOING TO NEXT ITEM" >> ${daily_log} 
        echo `exec date +%Y/%m/%d:%H:%M:%S` ${l1b_list[$ifile]} ' _F_' >> ${checkfile} 
        ((ifile=$ifile+1)) 
        continue

    else 

        echo `exec date +%Y/%m/%d:%H:%M:%S` "RUNNING OF POSTPROCESSING" ${postproc_driver} "SUCCESSFUL" >> ${daily_log} 

        # C.Schlundt, 13.05.2015 config_attributes.file: file_version='1.3'
        if [[ ${INSTRUMENT} = "AVHRR" ]]; then 

            typeset -u UPLATFORM=${PLATFORM} 
            finalfileprimary=${YEAR}${MONTHS}${DAYS}${HOUR}${MINUTE}00-ESACCI-L2_CLOUD-CLD_PRODUCTS-${INSTRUMENT}GAC-${UPLATFORM}-fv${file_version}.nc 
            finalcomb_out_path_primary=${l2_outp_post}/${finalfileprimary} 
            finalcomb_out_path_secondary=${l2_outp_post}/${finalfilesecondary} 

        elif [[ ${INSTRUMENT} = "MODIS" ]]; then 

            typeset -u UPLATFORM=${PLATFORM} 
            echo ${UPLATFORM} ${INSTRUMENT} 
            finalfileprimary=${YEAR}${MONTHS}${DAYS}${HOUR}${MINUTE}00-ESACCI-L2_CLOUD-CLD_PRODUCTS-${INSTRUMENT}-${UPLATFORM}-fv${file_version}.nc 
            finalfilesecondary=${YEAR}${MONTHS}${DAYS}${HOUR}${MINUTE}00-ESACCI-L2_CLOUD-CLD_PRODUCTS-${INSTRUMENT}-${UPLATFORM}-fv${file_version}.secondary.nc 
            finalcomb_out_path_primary=${l2_outp_post}/${finalfileprimary} 
            finalcomb_out_path_secondary=${l2_outp_post}/${finalfilesecondary} 
        fi 

    fi     
       

    echo  `exec date +%Y/%m/%d:%H:%M:%S` "PROCESSING OF ITEM" ${l1b_list[$ifile]} "FINISHED" >> ${daily_log}
    echo " " >> ${daily_log}
    echo `exec date +%Y/%m/%d:%H:%M:%S` ${l1b_list[$ifile]} ' _S_' >> ${checkfile}


    # -- if one element was processed go to next
    ((ifile=$ifile+1)) 

done

echo "#------------------------------------------#" >> ${daily_log}
echo "#------------------------------------------#" >> ${daily_log}
echo `exec date +%Y/%m/%d:%H:%M:%S` "PROCESSING OF DATE" \
${YEAR}${MONTHS}${DAYS} "OF" ${INSTRUMENT} "ON" ${PLATFORM} "WITH ID" ${ID} "FINISHED" \
>> ${daily_log}
echo "A TOTAL OF" ${ifile} "FILES OUT OF" ${nl1b} "WERE COMPLETED" >> ${daily_log}
echo "#------------------------------------------#" >> ${daily_log}
echo "#------------------------------------------#" >> ${daily_log}

daily_done=${LOGS_MONTHLY}/${DAYS}_jobdone_${ID}.done
touch ${daily_done}
echo 'DONE WITH DAILY SETUP FOR' ${YEAR}${MONTHS}${DAYS} ${itask} 

searchdir=${path_to_albedo}
type=alb
searchfile="${searchdir}/${YEAR}${MONTHS}${DAYS}_${type}_${ID}_listing.dat"
rm -f ${searchfile}

searchdir=${path_to_brdf}
type=brdf
searchfile="${searchdir}/${YEAR}${MONTHS}${DAYS}_${type}_${ID}_listing.dat"
rm -f ${searchfile}

searchdir=${path_to_ice}
type=is
searchfile="${searchdir}/${YEAR}${MONTHS}${DAYS}_${type}_${ID}_listing.dat"
rm -f ${searchfile}

searchdir=${path_to_emissivity}
type=em
searchfile="${searchdir}/${YEAR}${MONTHS}${DAYS}_${type}_${ID}_listing.dat"
rm -f ${searchfile}

    
# -- END --
