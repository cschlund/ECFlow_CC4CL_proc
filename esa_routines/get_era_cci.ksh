#!/bin/ksh
# 2014-04-08 MJ migration to cca/sf7
#

set -x

DATE=${1}
DATADIR=${2}
latIncr=${3}
lonIncr=${4}
gridInfoFile=${5}

export MARS_MULTITARGET_STRICT_FORMAT=1

TYPE=an
STEP=00

MONTHDIR=`exec dirname ${DATADIR}`
FILENAME_REMAPWEIGHTS=${MONTHDIR}/remapweights.nc

for TIME in 00 06 12 18; do

FILENAME_GRIB='"'${DATADIR}/ERA_Interim_${TYPE}_${DATE}_${TIME}+${STEP}.grb'"'
FILENAME_GRIB2='"'${DATADIR}/ERA_Interim_${TYPE}_${DATE}_${TIME}+${STEP}_HR.grb'"'
FILENAME_NETCDF='"'${DATADIR}/ERA_Interim_${TYPE}_${DATE}_${TIME}+${STEP}.nc'"'

echo "GET_ERA_CCI: Retrieve gribfile " $FILENAME_GRIB


[[ ${TIME} -eq 00 ]] && STIME=00:00:00
[[ ${TIME} -eq 06 ]] && STIME=06:00:00
[[ ${TIME} -eq 12 ]] && STIME=12:00:00
[[ ${TIME} -eq 18 ]] && STIME=18:00:00

mars << EOF

                      retrieve,
                            time=${STIME},
                            date=${DATE},
                            stream=oper,
                          # levtype=pl,
                            levtype=ml,
                          # levelist=100/200/300/400/500/600/700/850/925/1000,
                            levelist=all,
                            expver=1,
                            type=${TYPE},
                            step=${STEP},
                            class=ei,
                            param=129/130/133/152/203,
                            grid=${latIncr}/${lonIncr},
                            target=${FILENAME_GRIB}

                      retrieve,
                            time=${STIME},
                            date=${DATE},
                            stream=oper,
                            levtype=sfc,
                            expver=1,
                            type=${TYPE},
                            step=${STEP},
                            class=ei,
                            param=31/32/34/137/141/165/166/167/172/235,
                            grid=${latIncr}/${lonIncr},
                            target=${FILENAME_GRIB}

                      retrieve,
                            time=${STIME},
                            date=${DATE},
                            stream=oper,
                            levtype=sfc,
                            expver=1,
                            type=${TYPE},
                            step=${STEP},
                            class=ei,
                            param=31/141/235,
                            grid=0.1/0.1,
                            target=${FILENAME_GRIB2}

EOF

rc=$?
                    
if [ ${rc} -eq 0 ]; then 
    echo "The MARS ERA interim request for ${DATE} ran successfully at `date`!"
fi

if [ ${rc} -ge 1 ]; then 
    echo "ERROR: The MARS ERA interim request for ${DATE} FAILED at `date`!" 
    exit 1
fi

done

for TIME in 00 06 12 18; do 

    FILENAME_GRIB=${DATADIR}/ERA_Interim_${TYPE}_${DATE}_${TIME}+${STEP}.grb
    FILENAME_GRIB2=${DATADIR}/ERA_Interim_${TYPE}_${DATE}_${TIME}+${STEP}_HR.grb
    FILENAME_NETCDF=${DATADIR}/ERA_Interim_${TYPE}_${DATE}_${TIME}+${STEP}.nc
    FILENAME_NETCDF2=${DATADIR}/ERA_Interim_${TYPE}_${DATE}_${TIME}+${STEP}_HR.nc

    cdo -t ecmwf -f nc copy ${FILENAME_GRIB} ${FILENAME_NETCDF}    
    cdo -t ecmwf -f nc copy ${FILENAME_GRIB2} ${FILENAME_NETCDF2}    

    rc=$?
                        
    if [ ${rc} -eq 0 ]; then 
        echo "The MARS GRIB data converted successfully to NetCDF format for ${DATE}!" 
        rm -f ${FILENAME_GRIB}
        rm -f ${FILENAME_GRIB2}
    fi
    
    if [ ${rc} -ge 1 ]; then 
        echo "ERROR: The MARS GRIB data conversion to NetCDF format FAILED for ${DATE}!" 
        exit 1
    fi

    # Produce NetCDF file of remapping weights for ERA data.
    # This file is needed by CDO to remap ERA data onto
    # the preprocessing grid, and helps to double processing speed.
    # Do this only if file does not exist yet.
    if [[ ! -e ${FILENAME_REMAPWEIGHTS} ]] 
    then
	echo "Generating ERA-Interim remapping weights for ${DATE}"
	cdo gendis,${gridInfoFile} ${FILENAME_NETCDF} ${FILENAME_REMAPWEIGHTS}  
	rc2=$?
	if [ ${rc2} -eq 0 ]; then 
            echo "Remapping weights successfully created for ${DATE}!" 
	fi
    fi

    rc=$?
    #rc=1
    
    if [ ${rc} -eq 0 ]; then 
	echo "Now doing the actual remapping of file ${FILENAME_NETCDF}..."
	cdo remap,${gridInfoFile},${FILENAME_REMAPWEIGHTS} ${FILENAME_NETCDF} ${FILENAME_NETCDF}_temp
	rc2=$?
	if [ ${rc2} -eq 0 ]; then 
	    mv ${FILENAME_NETCDF}_temp ${FILENAME_NETCDF}
	fi
    fi

done

