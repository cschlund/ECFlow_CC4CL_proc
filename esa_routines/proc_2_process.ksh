#!/bin/ksh
#
# NAME
#       proc_2_process.ksh
#
# PURPOSE
#       Process ESA CCI clouds 
#       writes configfiles, .bat files + .cmd files for one month  
#
#
# HISTORY
#       2012-05-15  A.Kniffka DWD KU22
#                   created, following seviri reprocessing 
#                   parallelisation by J.Tan
#       2012-07-03  M. Jerg DWD KU22 extended for 
#                   ESA CLOUD CCI ECV PRODUCTION
#       2014-04-15 MJ migration to cca/sf7 Stage I
#       2014-11-26 C. Schlundt, adaption for ecflow
#

set -x

# default values for pbs
EC_tasks_per_node=1
EC_total_tasks=1
EC_threads_per_task=1
EC_hyperthreads=1
OMP_STACKSIZE=256M

# source config files
config_file_paths=${1}
. ${config_file_paths}
config_file_proc2=${2}
. ${config_file_proc2}
config_file_attributes=${3}
. ${config_file_attributes}

# set other parameters passed
YEAR=${4}
MONTH=${5}
MONTHS=$(printf %02d $MONTH)
STARTDAY=${6}
STOPDAY=${7}
instrument=${8}
platform=${9} 
id=${10}

echo $id

# create monthly log dir to store all parallel processing files and logs
logs_monthly=${LOGDIR}/processing/${YEAR}${MONTHS}_${instrument}_${platform}_${id}
mkdir -p ${logs_monthly} 

echo ${YEAR} ${MONTHS}

echo ${logs_monthly}

# initialize monthly .cmd
> ${logs_monthly}/process_single_day_${YEAR}${MONTHS}_${instrument}_${platform}_${id}.cmd


# LOOP OVER DAYS STARTS HERE
for DAY in $(seq ${STARTDAY} ${STOPDAY})
do 
    
DAYS=$(printf %02d $DAY)

#set path for daily output file
DAILY_PATH=${YEAR}${MONTHS}${DAYS}_${instrument}_${platform}_${id}
DAILY_OUTP=${OUTPUTDIR}/${DAILY_PATH}

# create logfile name for each day
daily_log=${logs_monthly}/process_single_day_${DAILY_PATH}.log

cinstr_channel_num=`echo '"'${instr_channel_num[*]}'"'`
cabs_channel_num=`echo '"'${abs_channel_num[*]}'"'`
cproc_flag=`echo '"'${proc_flag[*]}'"'`
cnchannels=`echo '"'${nchannels[*]}'"'`
cprod_name=`echo '"'${prod_name}'"'`

aatsr_drift="n/a"
ecmwf_path2="n/a"
ecmwf_path3="n/a"

# daily .config
echo " 
#
# ------------------------------------------------------------------
#
# configfile 2 of 2 for processing of a single day ESA CCI clouds
#
# ------------------------------------------------------------------
#

YEAR=${YEAR}
MONTH=${MONTH}
DAY=${DAY} 
INSTRUMENT=${instrument}
PLATFORM=${platform} 
ID=${id}
LOGS_MONTHLY=${logs_monthly}
DAILY_OUTP=${DAILY_OUTP}
gridflag=${gridflag}
dellon=${dellon}
dellat=${dellat}
channelflag=${channelflag}
teststartx=${teststartx}
testendx=${testendx}
teststarty=${teststarty}
testendy=${testendy}
testrun=${testrun}
nchannels=${cnchannels}
proc_flag=${cproc_flag}
minre_i=${minre_i}
minre_w=${minre_w}
maxre_i=${maxre_i}
maxre_w=${maxre_w}
minod_i=${minod_i}
minod_w=${minod_w}
maxod_i=${maxod_i}
maxod_w=${maxod_w}
maxcost=${maxcost}
costfactor=${costfactor}
cotthres=${cotthres}
cotthres1=${cotthres1}
cotthres2=${cotthres2}
lsec=${lsec}
lstrict=${lstrict}
tempthres_h=${tempthres_h}
tempthres_m=${tempthres_m}
tempthres_l=${tempthres_l}
tempthres1=${tempthres1}
ctt_bound=${ctt_bound}
ctt_bound_winter=${ctt_bound_winter}
ctt_bound_summer=${ctt_bound_summer}
ctt_thres=${ctt_thres}
ctp_thres=${ctp_thres}
ctp_thres1=${ctp_thres1}
ctp_bound=${ctp_bound}
ctp_bound_up=${ctp_bound_up}
ctp_udivctp=${ctp_udivctp}

daily_log=${daily_log}
prod_name=${cprod_name}
prod_type=${prod_type}
aatsr_drift=${aatsr_drift}
badc=${badc}
ecmwf_path2=${ecmwf_path2}
ecmwf_path3=${ecmwf_path3}
cchunkproc=${cchunkproc}
day_nightc=${day_nightc}
cverbose=${cverbose}
cchunk=${cchunk}
cfullpath=${cfullpath}
cfullbrdf=${cinclude_full_brdf}
rttov_version=${RTTOV_version}
ecmwf_version=${ECMWF_version}
svn_version=${SVN_version}
one_phase_only=${one_phase_only}
cloudy_only=${cloudy_only}

#END"> ${logs_monthly}/process_single_day_${DAILY_PATH}.config

done

# END of ksh script
