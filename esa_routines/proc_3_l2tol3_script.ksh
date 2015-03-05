#!/bin/ksh

 # Script to select and run the l2->l3 software for monthly means
 # 2012/02/03 Matthias Jerg cleans out prototype code to prepare repository upload.
 # 2014-04-08 MJ migration to cca/sf7

 set -x

 job_id=$1

 #define and read config files:
 #source path and attributes configfile
 . $2

 #source proc 3 configfile 
 . $3

 #source actual config file
 . $4

 algo=${l2processor}

 if [ "${sensor}" = MODIS ] ; then
    if [ "${platform}" = MYD ] ; then
       platform=AQUA
    fi
    if [ "${platform}" = MOD ] ; then
       platform=TERRA
    fi
 fi

 DOM=`cal ${MONTH} ${YEAR}  |tr -s " " "\n"|tail -1`

 MONTH=$(printf %02d $MONTH)

 #resolution 1/grid?
 if [[ "${prodtype}" = l2b || "${prodtype}" = l2b_sum ]] ; then
     if [ "${prodtype}" = l2b ] ; then
	    gridx=${gridxl2b}
	    gridy=${gridyl2b}
     else
	    gridx=${gridxl3}
	    gridy=${gridyl3}
     fi
     if [ ${DAY} = -1 ] ; then
	    loop_start=1
	    loop_count=${DOM}
     else
	    loop_start=${DAY}
	    loop_count=${DAY}
     fi
     # stored in daily config file: see "write_l3_mpmd_config_files.R"
     l2info_dum=${filelist_level2_output}
 else
     gridx=${gridxl3}
     gridy=${gridyl3}
     loop_start=1
     loop_count=1
     # use this path along with find to make file_list (max 31 files should be fast enough)
     l2info_dum=${l3outputpath}/${YEAR}${MONTH}*${sensor}*${platform}_L2B_SUM_*${id}/
 fi

 #present date and time for output file name
 exec_time=`exec date +%Y%m%d%H%M%S`

 #set $area
 if [ "${slon}" -lt 0 ] ; then
     lon_left=W
     let abs_slon=-1*${slon}
 else
     lon_left=E
     abs_slon=${slon}
 fi
 if [ "${elon}" -lt 0 ] ; then
     lon_right=W
     let abs_elon=-1*${elon}
 else
     lon_right=E
     abs_elon=${elon}
 fi
 if [ "${slat}" -lt 0 ] ; then
     lat_bot=S
     let abs_slat=-1*${slat}
 else
     lat_bot=N
     abs_slat=${slat}
 fi
 if [ "${elat}" -lt 0 ] ; then
     lat_top=S
     let abs_elat=-1*${elat}
 else
     lat_top=N
     abs_elat=${elat}
 fi

 abs_elat=$(printf %02d ${abs_elat})
 abs_slat=$(printf %02d ${abs_slat})
 abs_elon=$(printf %02d ${abs_elon})
 abs_slon=$(printf %02d ${abs_slon})

 area=${abs_slat}${lat_bot}${abs_elat}${lat_top}${abs_slon}${lon_left}${abs_elon}${lon_right}

 # loop for l2b days (use parallel instead)
 for DAY in `seq ${loop_start} ${loop_count}` ; do

 DAY=$(printf %02d $DAY)

 #l2b product
 if [ "${prodtype}" = l2b ] ; then
     datum=${YEAR}${MONTH}${DAY}
     prodtype_fn='L3U'
     DUR='P1D'
     summary=${summary_L2b}
     prod_name=daily_samples_global    
     #avhrr
     if [ "${sensor}" = AVHRR ] ; then
	     sensor_version=${sensor_version_avhrr}
	     #global/local
	     if [ "${local}" = T ] ; then
             prod_name=daily_samples_${area}
             gridx=${gridxloc}
             gridy=${gridyloc}
	     fi
     fi
     #modis
     if [ "${sensor}" = MODIS ] ; then
	     sensor_version=${sensor_version_modis}
	     #global/local
	     if [ "${local}" = T ] ; then
	         prod_name=daily_samples_${area}
	         gridx=${gridxloc}
	         gridy=${gridyloc}
	     fi
     fi
 fi

 #l2b_sum sum up for l3a
 if [ "${prodtype}" = l2b_sum ] ; then
    datum=${YEAR}${MONTH}${DAY}
    prodtype_fn='L2B_SUM'
    summary=${summary_L3}
    DUR='P1M'
    prod_name=monthly_means_global
    if [ "${sensor}" = AVHRR ] ; then
      sensor_version=${sensor_version_avhrr}
      if [ "${local}" = T ] ; then
         prod_name=monthly_means_${area}
         gridx=${gridxloc}
         gridy=${gridyloc}
      fi
    fi
    if [ "${sensor}" = MODIS ] ; then
       sensor_version=${sensor_version_modis}
       if [ "${local}" = T ] ; then
          prod_name=monthly_means_${area}
          gridx=${gridxloc}
          gridy=${gridyloc}
       fi
    fi
 fi

 # following runs on daily sums only "l2b_sum" 
 # l3a 
 if [ "${prodtype}" = l3a ] ; then
    datum=${YEAR}${MONTH}
    prodtype_fn='L3C'
    summary=${summary_L3}
    DUR='P1M'
    prod_name=monthly_means_global
    if [ "${sensor}" = AVHRR ] ; then
      sensor_version=${sensor_version_avhrr}
      if [ "${local}" = T ] ; then
         prod_name=monthly_means_${area}
         gridx=${gridxloc}
         gridy=${gridyloc}
      fi
    fi
    if [ "${sensor}" = MODIS ] ; then
       sensor_version=${sensor_version_modis}
       if [ "${local}" = T ] ; then
          prod_name=monthly_means_${area}
          gridx=${gridxloc}
          gridy=${gridyloc}
       fi
    fi
 fi

 if [ "${prodtype}" = l3b ]; then
    datum=${YEAR}${MONTH}
    prodtype_fn='L3S'
    DUR='P1M'
    summary=${summary_L3}
    prod_name=monthly_means_global
    if [ "${sensor}" = AVHRR ]; then
       platform=NOAAs_METOPs
       sensor_version=${sensor_version_avhrr}
       if [ "${local}" = T ] ; then
          prod_name=monthly_means_${area}
          gridx=${gridxloc}
          gridy=${gridyloc}
       fi
    fi
    if [ "${sensor}" = MODIS ] ; then
       platform=AQUA_TERRA
       sensor_version=${sensor_version_modis}
       if [ "${local}" = T ] ; then
          prod_name=monthly_means_${area}
          gridx=${gridxloc}
          gridy=${gridyloc}
       fi
    fi
fi

if [ "$prodtype" = l3c ] ; then
    datum=${YEAR}${MONTH}
    prodtype_fn='L3S'
    DUR='P1M'
    summary=${summary_L3}
    platform=ALL
    sensor_version=${sensor_version_modis}" and "${sensor_version_avhrr}
    prod_name=monthly_means_global
    if [ "${local}" = T ] ; then
       prod_name=monthly_means_${area}
       gridx=${gridxloc}
       gridy=${gridyloc}
    fi
fi

#this sets the sensor and platform names for the final filenames
#and for the netcdf attributes
#for modis everything is already set
sensor_fn=${sensor}
platform_fn=${platform}

#for avhrr overwrite to make conform with ds-wg req.
if [ "${sensor}" = AVHRR ] ; then
    case ${platform} in
    *"NOAA"*) plat=`exec echo ${platform} | cut -c1-4`
    num=`exec echo ${platform} | cut -c5-`
    platform_fn=${plat}-${num}
    ;;
    *) platform_fn=${platform} ;;
    esac
fi

source=${sensor_fn}_${platform_fn}_${sensor_version}

outputdir=${l3outputpath}/${datum}_${sensor}_${l2processor}V${l2proc_version}_${l3processor}V${l3proc_version}_${platform}_${prodtype_fn}_${prod_name}_${gridx}${gridy}_${file_version}_${job_id}
outputfile=${datum}-ESACCI-${prodtype_fn}_CLOUD-CLD_PRODUCTS-${sensor_fn}_${platform_fn}-fv${file_version}.nc

#files which contain the filelists the software works through then
mkdir -p ${outputdir}
l2info=${outputdir}/l2files_${exec_time}.tmp

#write file list
if [[ "${prodtype}" = l2b || "${prodtype}" = l2b_sum ]] ; then
   cat ${l2info_dum} | grep ${datum} > ${l2info}
else
   find ${l2info_dum} -type f -name "*.nc"  -exec ${ESA_ROUT}/add_dq.ksh '{}' \; > ${l2info}
fi

#olduuid_tag=`/perm/ms/de/sf7/esa_cci_c_proc/tools_bins/uuid_gen -t`
uuid_tag=`/perm/ms/de/sf7/esa_cci_c_proc/tools_bins/ossp_uuid-1.6.2/bin/uuid -v 4`

echo `date` 'preparation of names and lists finished, execute now l2->l3 processing for' ${datum}
echo ''
echo ${l3execpath}/l2tol3_script.x ${prodtype} "${sensor_fn}" "${algo}" "${l2info}" "${outputdir}/${outputfile}" ${gridx} ${gridy} ${uuid_tag} "${platform_fn}" ${exec_time} "${prod_name}" ${YEAR} ${MONTH} ${DAY} "${ncdf_version}" "${cf_convention}" "${processing_inst}" "${l2processor}" "${l2proc_version}" "${l3processor}" "${l3proc_version}" "${contact_email}" "${contact_website}" "${grid_type}" "${reference}" "${history}" "${summary}" "${keywords}" "${comment}" "${project}" "${file_version}" "${source}" ${DOM} "${DUR}" "${license}" "${standard_name_voc}" "${local}" "${slon}" "${elon}" "${slat}" "${elat}"
echo ''
#${l3execpath}/vfb.x
${l3execpath}/l2tol3_script.x ${prodtype} "${sensor_fn}" "${algo}" "${l2info}" "${outputdir}/${outputfile}" ${gridx} ${gridy} ${uuid_tag} "${platform_fn}" ${exec_time} "${prod_name}" ${YEAR} ${MONTH} ${DAY} "${ncdf_version}" "${cf_convention}" "${processing_inst}" "${l2processor}" "${l2proc_version}" "${l3processor}" "${l3proc_version}" "${contact_email}" "${contact_website}" "${grid_type}" "${reference}" "${history}" "${summary}" "${keywords}" "${comment}" "${project}" "${file_version}" "${source}" ${DOM} "${DUR}" "${license}" "${standard_name_voc}" "${local}" "${slon}" "${elon}" "${slat}" "${elat}"

if [ "${?}" -eq 0  ] ; then
   echo 'done L2->L3 finished, results written to: ' $outputdir/$outputfile
else
   echo 'run_l2tol3_script.ksh: Something went wrong! Read Error File!'
fi 

done

exit
