# these few lines write the driver file for
# the post processing of the current granule/orbit

echo "'${wat_out_path}.primary.nc'
'${ice_out_path}.primary.nc'
'${wat_out_path}.secondary.nc'
'${ice_out_path}.secondary.nc'
'${comb_out_path}.primary.nc'
'${comb_out_path}.secondary.nc'
${one_phase_only}
${cloudy_only}
${cotthres}
${cotthres1}
${cotthres2}
${proc_flag}
${INSTRUMENT}
${lsec}
${lstrict}
#END">${postproc_driver}
