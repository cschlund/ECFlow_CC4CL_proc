#these few lines write the driver file for
#the post processing of the current granule/orbit

echo "'${wat_out_path}.primary.nc'
'${ice_out_path}.primary.nc'
'${wat_out_path}.secondary.nc'
'${ice_out_path}.secondary.nc'
'${comb_out_path}.primary.nc'
'${comb_out_path}.secondary.nc'
${minre_w} ${minre_i}
${maxre_w} ${maxre_i}
${minod_w} ${minod_i}
${maxod_w} ${maxod_i}
${maxcost}
${costfactor}
${cotthres}
${cotthres1}
${cotthres2}
${proc_flag}
${sensor}
${lsec}
${lstrict}
${tempthres_h}
${tempthres_m}
${tempthres_l}
${tempthres1}
${ctt_bound}
${ctt_bound_winter}
${ctt_bound_summer}
${ctt_thres}
${ctp_thres}
${ctp_thres1}
${ctp_bound}
${ctp_bound_up}
${ctp_udivctp}
${uuid_tag_primary}
${uuid_tag_secondary}
${CPLATFORM}
${exec_time_pre}
${cprod_name}
${prod_type}
${ncdf_version}
${cf_convention}
${cprocessing_inst}
${l2processor}
${l2proc_version}
${contact_email}
${contact_website}
${reference}
${chistory}
${csummary}
${ckeywords}
${ccomment}
${cproject}
${clicense}
${file_version}
${source}
${file_name}
${cstandard_name_voc}
#END">${postproc_driver}
