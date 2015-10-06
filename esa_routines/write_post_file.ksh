# these few lines write the driver file for
# the post processing of the current granule/orbit

echo "'${wat_out_path}.primary.nc'
'${ice_out_path}.primary.nc'
'${wat_out_path}.secondary.nc'
'${ice_out_path}.secondary.nc'
'${comb_out_path}.primary.nc'
'${comb_out_path}.secondary.nc'
${switch_phases}
#END">${postproc_driver}
