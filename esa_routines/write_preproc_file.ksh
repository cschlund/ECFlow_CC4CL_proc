# '${l2proc_version}'
# these few lines write the driver file for
# the preprocessing of the current granule/orbit
echo "'${sensor}'
'${path_to_l1b}'
'${path_to_geo}'
'${path_to_USGS}'
'${ERA_before_satellite}'
'${path_to_coeffs}'
'${path_to_emiss_atlas}'
'${path_and_file_to_ice}'
'${path_and_file_to_albedo}'
'${path_and_file_to_brdf}'
'${path_and_file_to_emissivity}'
'${dellon}'
'${dellat}'
'${l2_outp_pre}' 
'${startx}'
'${endx}'
'${starty}'
'${endy}'
'${ncdf_version}'
'${cf_convention}'
'${processing_inst}'
'${l2processor}'
'${contact_email}'
'${contact_website}'
'${file_version}'
'${reference}'
'${history}'
'${summary}'
'${keywords}'
'${comment}'
'${project}'
'${license}'
'${uuid_tag}'
'${exec_time_pre}'
'${aatsr_drift}'
'${badc}'
'${ecmwf_path2}'
'${ecmwf_path3}'
'${cchunkproc}'
'${day_nightc}'
'${cverbose}'
'${cchunk}'
'${cfullpath}'
'${cfullbrdf}'
'${rttov_version}'
'${ecmwf_version}'
'${svn_version}'
ECMWF_PATH_FILE_2=${ERA_after_satellite}
#END">${preproc_driver}
