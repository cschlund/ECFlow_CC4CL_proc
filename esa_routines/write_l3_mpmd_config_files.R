## write config files for L3 production

## read command arguments
args = commandArgs( trailingOnly = T )

year         = args[2]
month        = args[3]
prodtype     = args[4]
sensor       = args[5]
platform     = args[6]
jobID        = args[7]
ndays        = args[8]
cfg_dir      = args[9]
cfg_prefix   = args[10]
cfg_suffix   = args[11]
cfg_base     = args[12]
base_path    = args[13]
flist_l2_out = args[14]
proc_toa     = args[15]
global_conf  = args[16]

print(global_conf)

global_values = read.table( global_conf, as.is=T, col.names = "values")
local = global_values$values[pmatch("local", global_values$values)]
local = unlist(strsplit(local, "="))[2]

## convert single digit months to double digits
month_mm = ifelse( nchar( month ) == 1, paste( "0", month, sep="" ), month )

## list L2 output folder matching filter criteria
L2_folder = list.files( base_path, pattern = paste( year, month_mm, "01_", sensor,
                                                   "_", platform, "_retrieval_*", sep="" ), ignore.case=T )

## if more than one matching output folder available, sort these as a function
## of creation time and select most recently created folder
if ( length( L2_folder ) > 1 ) {
    creation_time = file.info( paste( base_path, L2_folder, sep="/" ) )
    L2_folder = L2_folder[ order( creation_time$ctime, decreasing = T )[1] ]
}

## extract ID from L2 output folder
L2_id = paste( "ID", unlist( strsplit( L2_folder, "_ID" ) )[2], sep="" )

for (i in 1:ndays) {

    ## convert single digit days to double digits
    i_dd = as.character(i)
    i_dd = ifelse(nchar(i_dd) == 1, paste("0", i_dd, sep=""), i_dd)

    ## build config file name (consistent with write MPMD taskfile!)
    config_file = paste(cfg_dir, "/", cfg_prefix, cfg_base, i_dd, ifelse(local, "_Europe", ""), cfg_suffix, sep="")

    ## open config file connection
    fileConn = file( config_file )

    ## write data to config file
    writeLines( c(

        paste("YEAR=", year, sep=""),
        paste("MONTH=", month, sep=""),
        paste("DAY=", i, sep=""),
        paste("prodtype=", prodtype, sep=""),
        paste("sensor=", sensor, sep=""),
        paste("platform=", platform, sep=""),
        paste("filelist_level2_output=", flist_l2_out, sep=""),
        global_values$values[pmatch("local", global_values$values)],
        global_values$values[pmatch("slon", global_values$values)],
        global_values$values[pmatch("elon", global_values$values)],
        global_values$values[pmatch("slat", global_values$values)],
        global_values$values[pmatch("elat", global_values$values)],
        global_values$values[pmatch("gridxloc", global_values$values)],
        global_values$values[pmatch("gridyloc", global_values$values)],
        global_values$values[pmatch("gridxl3", global_values$values)],
        global_values$values[pmatch("gridyl3", global_values$values)],
        global_values$values[pmatch("gridxl2b", global_values$values)],
        global_values$values[pmatch("gridyl2b", global_values$values)],
        paste("proc_toa=", proc_toa, sep=""),
        paste("id=", L2_id, sep="")

    ), fileConn)

    ## close config file connection
    close(fileConn)

}
