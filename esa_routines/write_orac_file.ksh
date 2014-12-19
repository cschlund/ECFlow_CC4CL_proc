#these few lines write the driver file for
#the main processing of the current granule/orbit

echo "'${l2_outp_pre}'
'${preproc_base}'
'${l2_outp_main}'
'${path_to_sads}'
${sensor_platform}
${nchannels}
${proc_flag}
${phase}
#END">${mainproc_driver}

