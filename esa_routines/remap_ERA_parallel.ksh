#!/bin/ksh

set -x
module unload cdo
module load cdo/1.6.4

file=${1}
gridInfoFile=${2}
FILENAME_REMAPWEIGHTS=${3}

sep="+"
base=$(exec echo "${file}" | awk '{ print $1 }' | cut -f1 -d${sep})
end=$(exec basename "${file}" .grb | awk '{ print $1 }' | cut -f2 -d${sep})
cutoff=$(expr length ${base} - 2)
basecut=$(expr ${base} | cut -c -${cutoff})
file_HR=${base}${sep}${end}_HR.grb
FILENAME_NETCDF=${basecut}${sep}${end}.nc
FILENAME_NETCDF_HR=${basecut}${sep}${end}_HR.nc

cdo -t ecmwf -f nc copy "${file}" ${FILENAME_NETCDF}
rc=$?
if [ ${rc} -eq 0 ]; then 
    echo "MARS GRIB data converted successfully to NetCDF format for files ${file} (source) and ${FILENAME_NETCDF} (target)." 
    rm -f "${file}"
else
    echo "ERROR: MARS GRIB data conversion to NetCDF format FAILED for files ${file} (source) and ${FILENAME_NETCDF} (target)." 
    exit 1	
fi

cdo -t ecmwf -f nc copy "${file_HR}" ${FILENAME_NETCDF_HR}
rc=$?
if [ ${rc} -eq 0 ]; then 
    echo "MARS GRIB data converted successfully to NetCDF format for files ${file_HR} (source) and ${FILENAME_NETCDF_HR} (target)." 
    rm -f "${file_HR}"
else
    echo "ERROR: MARS GRIB data conversion to NetCDF format FAILED for files ${file_HR} (source) and ${FILENAME_NETCDF_HR} (target)." 
    exit 1	
fi

echo ${file}
cdo remap,${gridInfoFile},${FILENAME_REMAPWEIGHTS} ${FILENAME_NETCDF} ${FILENAME_NETCDF}_temp    
rc=$?
if [ ${rc} -eq 0 ]; then 
    echo "successfully remapped ${file}"
    mv ${FILENAME_NETCDF}_temp ${FILENAME_NETCDF}
else
    echo "ERROR: Remapping file ${file}." 
    exit 1	
fi
