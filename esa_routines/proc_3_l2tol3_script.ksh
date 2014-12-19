#!/bin/ksh

# Script to select and run the l2->l3 software for monthly means
# 2012/02/03 Matthias Jerg cleans out prototype code to prepare repository upload.
# 2014-04-08 MJ migration to cca/sf7

set -x

job_id=$1

# define and read config files:
# source path and attributes configfile
. $2

# source proc 3 configfile 
. $3

# source actual config file
. $4

# this sets some flags for the l3-from-l2b mode
if [ "${prodtype}" = l2b ] ; then fastl3=0; fi

if [ ${fastl3} -eq 0 ] ; then algo=${l2processor}; fi 
if [ ${fastl3} -eq 1 ] ; then algo=${l2processor}_L2B; fi 


# last day of month
DOM=`cal $MONTH $YEAR  |tr -s " " "\n"|tail -1`

if [ "${prodtype}" = l2b ] ; then

    gridx=${gridxl2b}
    gridy=${gridyl2b}

    if [ ${DAY} = -1 ] ; then 
        loop_start=1 
        loop_count=${DOM}
    else 
        loop_start=${DAY} 
        loop_count=${DAY}
    fi

else

    gridx=${gridxl3}
    gridy=${gridyl3}

    loop_start=1
    loop_count=1

fi


# present date and time for output file name
exec_time=`exec date +%Y%m%d%H%M%S`


# set $area
# slon --------------------------
if [ "${slon}" -lt 0 ]; then 
    lon_left=W 
    let abs_slon=-1*${slon} 
else
    lon_left=E
    abs_slon=${slon}
fi
# elon --------------------------
if [ "${elon}" -lt 0 ]; then 
    lon_right=W
    let abs_elon=-1*${elon} 
else
    lon_right=E
    abs_elon=${elon}
fi
# slat --------------------------
if [ "${slat}" -lt 0 ]; then 
    lat_bot=S
    let abs_slat=-1*${slat} 
else
    lat_bot=N
    abs_slat=${slat}
fi
# elat --------------------------
if [ "${elat}" -lt 0 ]; then
    lat_top=S
    let abs_elat=-1*${elat} 
else
    lat_top=N
    abs_elat=${elat}
fi

# abs_elat ----------------------
if [ "${abs_elat}" -le 9 ]; then 
    abs_elat=0${abs_elat}
fi
# abs_slat ----------------------
if [ "${abs_slat}" -le 9 ]; then 
    abs_slat=0${abs_slat}
fi
# abs_elon ----------------------
if [ "${abs_elon}" -le 9 ]; then 
    abs_elon=0${abs_elon}
fi
# abs_slon ----------------------
if [ "${abs_slon}" -le 9 ]; then 
    abs_slon=0${abs_slon}
fi


# finally area is:
area=${abs_slat}${lat_bot}${abs_elat}${lat_top}${abs_slon}${lon_left}${abs_elon}${lon_right}


# loop for l2b days
set -A dumday `seq -w 0 31`

MONTH=${dumday[${MONTH}]}

# -- for loop --
for i in `seq ${loop_start} ${loop_count}` ; do 

    DAY=${dumday[${i}]} 
    
    #----------------------------------------------
    # -- l2b product --
    #----------------------------------------------
    if [ "${prodtype}" = l2b ] ; then 
    
        datum=${YEAR}${MONTH}${DAY}
        prodtype_fn='L3U' 
    

        if [ "${sensor}" = AVHRR ] ; then 

            sensor_version=${sensor_version_avhrr} 

            if [ "${local}" = F ]; then 
                prod_name=daily_samples_global
                gridx=10 
                gridy=10 
            else 
                prod_name=daily_samples_${area} 
                gridx=10 
                gridy=10 
            fi 

        fi 


        if [ "${sensor}" = MODIS ] ; then 

            if [ "${platform}" = MYD ] ; then 
                platform=AQUA 
            fi 

            if [ "${platform}" = MOD ] ; then 
                platform=TERRA 
            fi 

            if [ "${local}" = F ]; then 
                prod_name=daily_samples_global
                gridx=10 
                gridy=10 
            else 
                prod_name=daily_samples_${area} 
                gridx=30 
                gridy=30 
            fi 

            sensor_version=${sensor_version_modis} 

        fi 


        DUR='P1D' 
        searchsubstring=${datum}*${sensor}*${platform}*.nc 
        summary=${summary_L2b} 

    fi 
    

    #----------------------------------------------
    # -- l3a product --
    #----------------------------------------------
    if [ "${prodtype}" = l3a ]; then 

        datum=${YEAR}${MONTH} 
        prodtype_fn='L3C' 
        
        if [ "${sensor}" = AVHRR ]; then 

            sensor_version=${sensor_version_avhrr} 

            if [ "${local}" = F ]; then 
                gridx=2 
                gridy=2 
                prod_name=monthly_means_global 
            else 
                prod_name=monthly_means_${area} 
                gridx=5 
                gridy=5 
            fi 

        fi 


        if [ "${sensor}" = MODIS ]; then 

            if [ "${platform}" = MYD ]; then 
                platform=AQUA 
            fi 

            if [ "${platform}" = MOD ] ; then 
                platform=TERRA 
            fi 

            if [ "${local}" = F ]; then 
                gridx=2 
                gridy=2 
                prod_name=monthly_means_global 
            else 
                prod_name=monthly_means_${area} 
                gridx=20 
                gridy=20 
            fi 

            sensor_version=${sensor_version_modis} 
        fi 

        summary=${summary_L3} 
        DUR='P1M' 
        searchsubstring=${datum}*${sensor}*${platform}*.nc 

        # for the time being name the l3-from-l2b products "experimental" 
        # adapt a new searchstring to find the l2b files instead of l2 files.  
        if [ ${fastl3} -eq 1 ] ; then 

            prod_name=${prod_name}_experimental 

            if [ "${sensor}" = MODIS ] ; then 
                searchsubstring=${datum}*L3U*${sensor}*${platform}*.nc 
            fi 

            if [ "${sensor}" = AVHRR ] ; then 
                #works only in bash 
                #name=`exec echo ${platform//[0-9]/}` 
                #number=`exec echo ${platform//[a-z]/}` 
                number=`echo ${platform##*[A-Z]}` 
                name=`echo ${platform%%[0-9]*}` 
                platformsearch=${name}'-'${number} 
                searchsubstring=${datum}*L3U*${sensor}*${platformsearch}*.nc 
            fi 
        fi 
    fi 


    #----------------------------------------------
    # -- L3b product --
    #----------------------------------------------
    if [ "${prodtype}" = l3b ]; then 

        datum=${YEAR}${MONTH} 
        searchsubstring=${datum}*${sensor}*.nc 
        prodtype_fn='L3S' 


        if [ "${sensor}" = AVHRR ]; then 

            platform=NOAAs_METOPs 

            if [ "${local}" = F ]; then 
                gridx=2 
                gridy=2 
                prod_name=monthly_means_global 
            else 
                prod_name=monthly_means_${area} 
                gridx=5 
                gridy=5 
            fi 

            sensor_version=${sensor_version_avhrr} 
        fi 


        if [ "${sensor}" = MODIS ] ; then 

            platform=AQUA_TERRA 
            sensor_version=${sensor_version_modis} 

            if [ "${local}" = F ]; then 
                gridx=2 
                gridy=2 
                prod_name=monthly_means_global 
            else 
                prod_name=monthly_means_${area} 
                gridx=20 
                gridy=20 
            fi 

        fi 

        DUR='P1M' 
        summary=${summary_L3} 

    fi 
    
    
    #----------------------------------------------
    # -- l3c product --
    #----------------------------------------------
    if [ "$prodtype" = l3c ] ; then 

        prodtype_fn='L3S' 
        platform=ALL 
        sensor_version=${sensor_version_modis}" and "${sensor_version_avhrr} 
        datum=${YEAR}${MONTH} 
        searchsubstring=${datum}*.nc 

        if [ "${local}" = F ]; then 
            gridx=2 
            gridy=2 
            prod_name=monthly_means_global 
        else 
            prod_name=monthly_means_${area} 
        fi 

        DUR='P1M' 
        summary=${summary_L3} 

    fi 


    # this sets the sensor and platform names for the final filenames 
    # and for the netcdf attributes for modis everything is already set 
    sensor_fn=${sensor} 
    platform_fn=${platform}

    # for avhrr overwrite to make conform with ds-wg req.
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
    parallel=0 # maybe later 

    outputdir=${l3outputpath}/${datum}_${sensor}_${l2processor}V${l2proc_version}_${l3processor}V${l3proc_version}_${platform}_${prodtype_fn}_${prod_name}_${gridx}${gridy}_${file_version}_${job_id} 

    outputfile=${datum}-ESACCI-${prodtype_fn}_CLOUD-CLD_PRODUCTS-${sensor_fn}_${platform_fn}-fv${file_version}.nc

    # files which contain the filelists the software works through then
    l2info=${outputdir}/l2files_${exec_time}.tmp


    # select the find commands appropriately
    if [ ${fastl3} -eq 0 ] ; then 
        nfiles=`find ${l2inputpath}/${datum}*${id}/ -type f -name ${searchsubstring} | wc -l` 
    fi 

    if [ ${fastl3} -eq 1 ] ; then 
        nfiles=`find ${l3outputpath}/* -type f -name ${searchsubstring} | wc -l` 
    fi
    
    
    if [ ${nfiles} != 0 ] ; then 

        mkdir -p ${outputdir} 
        echo ${nfiles} > $l2info 
        echo `date` "write file list to " ${l2info} 

        # select the find commands appropriately 
        if [ ${fastl3} -eq 0 ] ; then 
            find ${l2inputpath}/${datum}*${id}* -type f -name ${searchsubstring}  -exec ${ESA_ROUT}/add_dq.ksh '{}' \; >> ${l2info} 
        fi 

        if [ ${fastl3} -eq 1 ] ; then 
            find ${l3outputpath}/* -type f -name ${searchsubstring}   -exec ${ESA_ROUT}/add_dq.ksh '{}' \; >> ${l2info} 
        fi 

        uuid_tag=`/perm/ms/de/sf7/esa_cci_c_proc/tools_bins/ossp_uuid-1.6.2/bin/uuid -v 4` 

        echo 'preparation of names and lists finished, execute now l2->l3 processing for' ${datum} 

        echo ${l3execpath}/l2tol3_script.x "${LOCAL_L2TOL3CONFIGPATH}" "${LOCAL_L2TOL3CONFIGFILE}" ${prodtype} "${sensor_fn}" "${algo}" ${l1closure} "${l2info}" "${outputdir}/${outputfile}" ${gridx} ${gridy} ${uuid_tag} "${platform_fn}" ${exec_time} "${prod_name}" ${YEAR} ${MONTH} ${DAY} "${ncdf_version}" "${cf_convention}" "${processing_inst}" "${l2processor}" "${l2proc_version}" "${l3processor}" "${l3proc_version}" "${contact_email}" "${contact_website}" "${grid_type}" "${reference}" "${history}" "${summary}" "${keywords}" "${comment}" "${project}" "${file_version}" "${source}" ${DOM} "${DUR}" "${license}" "${standard_name_voc}" "${local}" "${slon}" "${elon}" "${slat}" "${elat}" 

        echo '' 

        ${l3execpath}/l2tol3_script.x "${LOCAL_L2TOL3CONFIGPATH}" "${LOCAL_L2TOL3CONFIGFILE}" ${prodtype} "${sensor_fn}" "${algo}" ${l1closure} "${l2info}" "${outputdir}/${outputfile}" ${gridx} ${gridy} ${uuid_tag} "${platform_fn}" ${exec_time} "${prod_name}" ${YEAR} ${MONTH} ${DAY} "${ncdf_version}" "${cf_convention}" "${processing_inst}" "${l2processor}" "${l2proc_version}" "${l3processor}" "${l3proc_version}" "${contact_email}" "${contact_website}" "${grid_type}" "${reference}" "${history}" "${summary}" "${keywords}" "${comment}" "${project}" "${file_version}" "${source}" ${DOM} "${DUR}" "${license}" "${standard_name_voc}" "${local}" "${slon}" "${elon}" "${slat}" "${elat}" 

        echo 'done L2->L3 finished, results written to: ' $outputdir/$outputfile 

    else 

        echo "Failed to create "${prodtype_fn}" File for "${datum}". No input files found! " 

    fi 

# --------------------- 
done
# -- end of for loop --

exit
