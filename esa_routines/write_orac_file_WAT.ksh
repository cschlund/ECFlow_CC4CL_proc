# these few lines write the driver file for
# the main processing of the current granule/orbit

echo "'${l2_outp_pre}'
'${preproc_base}'
'${l2_outp_main}'
'${path_to_sads}'
${sensor_platform}
${nchannels}
${proc_flag}
${phase}
CTRL%PROCESS_CLOUDY_ONLY=${cloudy_only}
CTRL%NTYPES_TO_PROCESS=${ntypes_to_process_WAT}
CTRL%TYPES_TO_PROCESS=${types_to_process_WAT}
CTRL%RS%USE_FULL_BRDF=${cfullbrdf}
#END">${mainproc_driver}

