# R script to read in AVHRR database orbit list for each day
# of a month; entries in daily lists are summed up to calculate
# total number of AVHRR orbits to be processed for given month

# called by set_cpu_number.ecf

# define function for counting number of days per month

numberOfDays = function(date) {
    m = format(date, format="%m")
    while (format(date, format="%m") == m) {
        date = date + 1
    }
    return(as.integer(format(date - 1, format="%d")))
}

# read command arguments
args = commandArgs( trailingOnly = T )

# define argument list
work_dir     = args[ 2 ]
output_file  = args[ 3 ]
gacdb_client = args[ 4 ]
dbfile       = args[ 5 ]
year         = args[ 6 ]
month 	     = args[ 7 ]
satellite    = toupper( args[ 8 ] )

# remove previous output_file
if ( file.exists( output_file ) ) foo = file.remove( output_file )

# create date for last day of previous month
previous.date = as.Date(paste(year, month, "01", sep="-"), "%Y-%m-%d") - 1
# extract year and month from previous day's date
previous.year  = format(previous.date,"%Y")
previous.month = format(previous.date,"%m")
previous.yyyymm = paste(previous.year, previous.month, sep="")

# get number of days in month to be processed
ndays = numberOfDays( as.Date(paste(year, month, "01", sep="-"), "%Y-%m-%d") )

daily_list = paste( work_dir, "daily_list.txt" , sep="" )
      
# loop over each day of month
for ( day in 1:ndays ){

    dday = as.character( day )
    dday = ifelse( day < 10, paste("0", dday, sep=""), dday )
    date = paste(year, month, dday, sep="")

    # call python GAC database client
    system.call = paste("python ", gacdb_client, " --dbfile=", dbfile,
                        " get_scanlines --date=", date, " --sat=", satellite,
	    " --mode=l1c > ", daily_list, sep="")
    system( system.call )

    # read first line to check if header text is available
    header = readLines( daily_list, n = 2 )
    # skip first line if header contains "[DEBUG" string
    # (should be extended for any rows starting with characters)
    nheader = ifelse ( strtrim( header[1] , 6 ) == "[DEBUG" , 1 , 0 )

    # read data and skip potential header rows
    tryCatch(
        {
            data = read.table( daily_list, skip = nheader )
        
            # only keep rows that contain non-negative scanline indexes 
            out  = data[ data[ , 3 ] >= 0 & data[ , 4] >= 0 , ]

            # exclude overlap orbit if from previous month (L1 data will have been deleted)
            if ( day==1 ){
                yyyymm = strtrim(out$V1,6)
                day_one_overlap = match(previous.yyyymm, yyyymm)
                if ( !is.na( day_one_overlap ) ){
                remove = which(previous.yyyymm == yyyymm)
                out = out[ -remove, ] 
                }
            }
                
            # write clean output data to file
            write.table( out , file = output_file , row.names = F , 
                    col.names = F , quote = F , sep = ",", append = T )

            # remove temporary file
            foo = file.remove( daily_list )
        }, 
    error=function(e)
        {
            if ( file.exists( daily_list ) ) foo = file.remove( daily_list )
        }
    )  

}

# return count of number of lines in output list
if ( file.exists( output_file ) ) {
    cat( length( scan( output_file, what = 'character', quiet = T ) ) )
} else {
    cat( "ERROR in count_AVHRR_orbits.R - no value returned" )
}
