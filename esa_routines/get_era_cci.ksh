#!/bin/ksh
# 2014-04-08 MJ migration to cca/sf7
#

set -x

YEAR=${1}
MONTH=${2}
DATADIR=${3}
latIncr=${4}
lonIncr=${5}
gridInfoFile=${6}

export MARS_MULTITARGET_STRICT_FORMAT=1

TYPE=an
STEP=00

DATE=$YEAR$MONTH

ndays=`cal ${MONTH} ${YEAR} | egrep -v [a-z] | wc -w`
dates=""

for f in {1..$ndays}; do 
    ff=`expr $(printf %02d $f)`
    if [[ ${f} == ${ndays} ]]; then
	dates=${dates}${YEAR}${MONTH}${ff}
    else
	dates=${dates}${YEAR}${MONTH}${ff}/
    fi
done

FILENAME_REMAPWEIGHTS=${DATADIR}/remapweights.nc
FILENAME_GRIB='"'${DATADIR}/ERA_Interim_${TYPE}_[date]_[time]+${STEP}.grb'"'
FILENAME_GRIB2='"'${DATADIR}/ERA_Interim_${TYPE}_[date]_[time]+${STEP}_HR.grb'"'

echo "GET_ERA_CCI: Retrieve gribfile " $FILENAME_GRIB

mars << EOF

                      retrieve,
                            time=00/06/12/18,
                            date=${dates},
                            stream=oper,
                            levtype=ml,
                            levelist=all,
                            expver=1,
                            type=${TYPE},
                            step=${STEP},
                            class=ei,
                            param=129/130/133/152/203,
                            grid=${latIncr}/${lonIncr},
                            target=${FILENAME_GRIB}

                      retrieve,
                            time=00/06/12/18,
                            date=${dates},
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
                            time=00/06/12/18,
                            date=${dates},
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
    echo "The MARS ERA interim request for ${YEAR}${MONTH} ran successfully!"
fi

if [ ${rc} -ge 1 ]; then 
    echo "ERROR: The MARS ERA interim request for ${DATE} FAILED" 
    exit 1
fi

sep="+"
for file in ${DATADIR}/*grb; do 
    base=`exec echo "${file}" | awk '{ print $1 }' | cut -f1 -d${sep}`
    end=`exec basename "${file}" .grb | awk '{ print $1 }' | cut -f2 -d${sep}`
    cutoff=`expr length ${base} - 2`
    basecut=`expr ${base} | cut -c -${cutoff}`
    FILENAME_NETCDF=${basecut}${sep}${end}.nc
    cdo -t ecmwf -f nc copy "${file}" ${FILENAME_NETCDF}
    rc=$?
    if [ ${rc} -eq 0 ]; then 
        echo "MARS GRIB data converted successfully to NetCDF format for files ${file} (source) and ${FILENAME_NETCDF} (target)." 
        rm -f "${file}"
    else
        echo "ERROR: MARS GRIB data conversion to NetCDF format FAILED for files ${file} (source) and ${FILENAME_NETCDF} (target)." 
        exit 1	
    fi
done

# Produce NetCDF file of remapping weights for ERA data.
# This file is needed by CDO to remap ERA data onto
# the preprocessing grid, and helps to double processing speed.
# Do this only if file does not exist yet.
if [[ ! -e ${FILENAME_REMAPWEIGHTS} ]] 
then
    FILENAME_NETCDF=`find $DATADIR -type f \( -iname "*.nc" ! -iname "*HR.nc" \) | head -n 1`
    echo "Generating ERA-Interim remapping weights for ${DATE}"
    echo "Input file = "${FILENAME_NETCDF}", output file = "${FILENAME_REMAPWEIGHTS}  
    cdo gendis,${gridInfoFile} ${FILENAME_NETCDF} ${FILENAME_REMAPWEIGHTS}  
    rc=$?
    if [ ${rc} -eq 0 ]; then 
        echo "Remapping weights successfully created for ${DATE}!" 
    else
	echo "ERROR: Creating remapping weights FAILED ${DATE}!" 
	exit 1
    fi
fi

set -A to_be_remapped `find $DATADIR -type f -iname "*00.nc"`
nremap=`expr ${#to_be_remapped[*]} - 1`

for f in {0..$nremap}; do 
    echo ${to_be_remapped[$f]}
    cdo remap,${gridInfoFile},${FILENAME_REMAPWEIGHTS} ${to_be_remapped[$f]} ${to_be_remapped[$f]}_temp    
    rc=$?
    if [ ${rc} -eq 0 ]; then 
	echo "successfully remapped ${to_be_remapped[$f]}"
 	mv ${to_be_remapped[$f]}_temp ${to_be_remapped[$f]}
    else
	echo "ERROR: Remapping file ${to_be_remapped[$f]}." 
	exit 1	
    fi
done
