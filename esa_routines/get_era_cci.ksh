#!/bin/ksh
# 2014-04-08 MJ migration to cca/sf7
#

DATE=${1}
DATADIR=${2}


export MARS_MULTITARGET_STRICT_FORMAT=1

TYPE=an
#TYPE=fc

STEP=00
#STEP=12

#for YEAR in 2008; do 
#for MONTH in 03; do
#for DAY in 20; do

#DATE=${YEAR}${MONTH}${DAY}

#for DATE in 20080320 20080613 20080620 20080921 20082012; do

for TIME in 00 06 12 18; do
#for TIME in 12; do

FILENAME_GRIB='"'${DATADIR}/ERA_Interim_${TYPE}_${DATE}_${TIME}+${STEP}.grb'"'
FILENAME_NETCDF='"'${DATADIR}/ERA_Interim_${TYPE}_${DATE}_${TIME}+${STEP}.nc'"'

echo "GET_ERA_CCI: Retrieve gribfile " $FILENAME_GRIB

#return 0

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
                            grid=0.75/0.75,
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
                            grid=0.75/0.75,
                            target=${FILENAME_GRIB}

EOF

rc=$?
                    
if [ ${rc} -eq 0 ]
then
echo "The MARS ERA interim request for ${DATE} ran successfully at `date`!"
fi

if [ ${rc} -ge 1 ]
then
echo "ERROR: The MARS ERA interim request for ${DATE} FAILED at `date`!"
  exit 1
fi

#TIME
done

for TIME in 00 06 12 18; do
#for TIME in 12; do

FILENAME_GRIB=${DATADIR}/ERA_Interim_${TYPE}_${DATE}_${TIME}+${STEP}.grb
FILENAME_NETCDF=${DATADIR}/ERA_Interim_${TYPE}_${DATE}_${TIME}+${STEP}.nc

cdo -t ecmwf -f nc copy ${FILENAME_GRIB} ${FILENAME_NETCDF}

rc=$?
                    
if [ ${rc} -eq 0 ]
then
echo "The MARS GRIB data converted successfully to NetCDF format for ${DATE}!"
rm -f ${FILENAME_GRIB}
fi

if [ ${rc} -ge 1 ]
then
echo "ERROR: The MARS GRIB data conversion to NetCDF format FAILED for ${DATE}!"
  exit 1
fi

done

#DATE
#done

#DAY
#done

#MONTH
#done

#YEAR
#done
