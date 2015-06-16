#!/bin/ksh
#
# ##############################################################################
#
# NAME
#       proc_1_get_data_avhrr.ksh
#
# PURPOSE
#       Extract AVHRR data from ECFS
#       gets one month of data
#
# HISTORY
#       2012-05-11  A.Kniffka DWD KU22
#           created
#       2012-06-12  M.JERG DWD KU22
#           modified to only extract AVHRR
#       2012-06-20 S.Stapelberg DWD KU22
#           untar data to $datadir rm tar if succesful
#           only one while loop left now for unix seconds -- not working at ECMWF!!!
#       2012-06-21 S.Stapelberg
#           different unixseconds approach works now at ECMWF
#           needs extra function ymdhms2unix.ksh
#	2012-07-11 S.Stapelberg
#	    added STARTDAY and STOPDAY to configfile 
#           gets now data of a single day ; if wanted
#   2014-04-08 MJ migration to cca/sf7
#   2014-11-12 C. Schlundt: modified in order to get new AVHRR GAC L1C data
#   2015-01-14 C. Schlundt: ahvrr_top added
#   2015-02-24 C. Schlundt: check data availability before ecp call
#
# ##############################################################################


# -- 2014-11-12 C. Schlundt
#    get AVHRR GAC L1C data processed by pyGAC
#    ARG1=year, ARG2=month, ARG3=satellite

get_avhrr_data()
{
 YEAR=${1}
 MONTH=$(printf %02d ${2})
 SAT=`echo ${3} | awk '{ print toupper($0)}'`
 ecfs_dir=${4}

 tar_prefix="AVHRR_GAC_L1C_"
 tar_suffix=".tar"
 bz2_suffix=".tar.bz2"
 
 ecfs_path="${ecfs_dir}/${YEAR}/${MONTH}"
 ecfs_file="${ecfs_path}/${tar_prefix}${SAT}_${YEAR}${MONTH}${tar_suffix}"
 
 tarfile=$(els ${ecfs_file})

 if [ ${?} -eq 0 ]; then
     print " * get ${tarfile}"

     # -- create input directory
     download_dir="${INPUTDIR}/AVHRR/${platform}/${YEAR}/${MONTH}"
     mkdir -p ${download_dir}

     print `print Start of dearchiving:` `date`

     # -- download file
     ecp ${ecfs_file} ${download_dir}

     print `print End of dearchiving:` `date`

     if [ ${?} -ne 0 ]; then
         print " --- FAILED: Download of ${ecfs_file} ! "
         return 1
     fi

     # -- extract monthly tarfile, 
     #    e.g. AVHRR_GAC_L1C_NOAA15_200801.tar
     cd ${download_dir}

     print `print Start of monthly tar file extraction:` `date`

     tar xf ${tarfile} && rm -f ${tarfile}

     print `print End of monthly tar file extraction:` `date`

     # -- extract daily zip files
     pattern="${tar_prefix}${SAT}_${YEAR}${MONTH}*${bz2_suffix}"
     zip_files=$(ls ${pattern})

     print `print Start of daily tar file extraction:` `date`

     for zipfile in ${zip_files}
     do
         print " * Working on: ${zipfile}"

         # -- extract day from zipfile
         fbase=`echo ${zipfile} | cut -d '.' -f1`
         split=`echo ${fbase} | cut -d "_" -f5`
         fday=`echo ${split} | cut -c 7-8`

         # -- create final input directory
         final_dir="${download_dir}/${fday}/${YEAR}${MONTH}${fday}"
         mkdir -p ${final_dir}

         # -- move zipfile to final dir.
         mv ${zipfile} ${final_dir}

         # -- extract files
         cd ${final_dir}
         tar xfj ${zipfile} && rm -f ${zipfile}
         cd ${download_dir}
     done

     print `print End of daily tar file extraction:` `date`

 else
     print " * no file available for $YEAR, $MONTH, $SAT"
     return 1
 fi

}

#-----------------------------------------------------------------------------

#
# Main
#
# input/sensor/platform/yyyy/mm/dd/yyyymmdd/*h5

set -xv

#source path configfile 
. $1

#source proc 1 configfile
. $2

# 2014-11-12 C. Schlundt: added
for year in `seq $STARTYEAR $STOPYEAR`
do
    for month in `seq $STARTMONTH $STOPMONTH`
    do 
        # availability flag
        aflag=-1

        # test if data is already on $SCRATCH
        mm=$(printf %02d ${month})
        target=$INPUTDIR/$instrument/$platform/$year/$mm

        if [ -d $target ]; then 
            echo "YES: $target exists"

            ndays=$(ls -A $target |wc -l)
            echo "Number of days: $ndays"

            if [ $ndays -gt 0 ]; then

                nfiles=$(ls -A $target/*/*/*avhrr* |wc -l)
                echo "Number of files: $nfiles"

                if [ $nfiles -gt 0 ]; then
                    aflag=0
                fi

            fi
        fi


        if [ $aflag -ne 0 ]; then
            echo "No data available on scratch, so get them!"

            params="$year $month $platform $avhrr_top"

            get_avhrr_data $year $month $platform $avhrr_top

            if [ ${?} -ne 0 ]; then
                print " --- FAILED: get_avhrr_data $params"
                return 1
            else
                print " --- FINISHED: get_avhrr_data $params"
            fi
        else 
            echo "There is nothing to do for $target" 
            echo "Data already available on scratch!"
        fi

    done # end of month loop
done # end of year loop

# -- end of ksh script
