# R script to read in AVHRR database orbit list for a single day
# returns list of AVHRR orbits to be processed

# called by process_single_day.ksh

# read command arguments
args = commandArgs( trailingOnly = T )

# define argument list
gacdb_client      = args[ 2 ]
dbfile            = args[ 3 ]
current.year      = args[ 4 ]
current.month     = args[ 5 ]
current.day       = args[ 6 ]
satellite         = toupper( args[ 7 ] )
orbits_file       = args[ 8 ]
l1_base_directory = args[ 9 ]
avhrr.sunsat.qual = args[ 10 ]

# create date for previous day
previous.date.temp = as.Date(paste(current.year, current.month, current.day, sep="-"), "%Y-%m-%d") - 1
# extract year, month, and day from previous day's date
previous.year  = format(previous.date.temp,"%Y")
previous.month = format(previous.date.temp,"%m")
previous.day   = format(previous.date.temp,"%d")

# build date string for current and previous day
current.date  = paste(current.year,  current.month,  current.day, sep="")
previous.date = paste(previous.year, previous.month, previous.day, sep="")

                                        # call python GAC database client (but only do for first run, i.e. when "avhrr" data are listed)
system.call = paste("python ", gacdb_client, " --dbfile=", dbfile,
                    " get_scanlines --date=", current.date, " --sat=", satellite,
                    " --mode=l1c > ", orbits_file, sep="")
# only call database if output file does not exist
if ( ! file.exists( orbits_file ) ) system( system.call )

# read first line to check if header text is available
header = readLines( orbits_file , n = 2 )
# skip first line if header contains "[DEBUG" string
# (should be extended for any rows starting with characters)
nheader = ifelse ( strtrim( header[1] , 6 ) == "[DEBUG" , 1 , 0 )

# read data and skip potential header rows
tryCatch(
{
    data = read.table( orbits_file , skip = nheader )
    # only keep rows that contain non-negative scanline indexes 
    out  = data[ data[ , 3 ] >= 0 & data[ , 4] >= 0 , ]
}, 
    error=function(e){}
)

# extract timestamp vector from data
timestamp_start = out$V1
timestamp_end   = out$V2

# build L1 directory and file list for current day
l1_directory_current_day = paste(l1_base_directory, current.year, current.month,
                                 current.day, current.date, sep="/")
l1_files_current_day = list.files(l1_directory_current_day)
# build L1 directory and file list for previous day
l1_directory_previous_day = paste(l1_base_directory, previous.year, previous.month,
                                  previous.day, previous.date, sep="/")
l1_files_previous_day = list.files(l1_directory_previous_day)

# create output vectors
#l1_file_index = l1_files = 1:length(timestamp_start)
l1_files = rep("", length(timestamp_start) )

pattern = avhrr.sunsat.qual

# loop over all timestamps
for ( i in 1 : length( timestamp_start ) ){

    # copy L1 data of previous day if orbit starts at previous day
    if ( strtrim( timestamp_start[i], 8 ) == previous.date ) {
        
        # get indexes of matching L1 files
        index = grep( paste( pattern, ".*", timestamp_start[i], "_", timestamp_end[i], sep=""),
                           l1_files_previous_day)[1]        

        # build paths of files to be copied
        from = paste( l1_directory_previous_day, "/",
                           l1_files_previous_day[index], sep="")        

        # build paths of destination files
        to = paste( l1_directory_current_day, "/",
                           l1_files_previous_day[index], sep="")        
        
        # copy overlap orbit of previous day into folder of current day
        file.copy( from, to )        

        # add file paths to output vectors
        l1_files[i] = to        
        
    } else {

        # get indexes of matching L1 files
        index = grep( paste( pattern, ".*", timestamp_start[i], "_",
                            timestamp_end[i], sep="" ), l1_files_current_day)[1]
        l1_files[i] = paste( l1_directory_current_day, "/", 
                            l1_files_current_day[index], sep="")
        
    }

}

# return l1 file list to shell
cat( l1_files )

