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
CTRL%PROCESS_ONE_PHASE_ONLY=${one_phase_only}
#END">${mainproc_driver}

