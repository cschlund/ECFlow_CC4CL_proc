## R script to write grid information file
## needed by CDO to remap ERA-Interim
## data on preprocessing grid

args = commandArgs(trailingOnly = T)

## define argument list
xinc         = as.numeric(args[2])
yinc         = as.numeric(args[3])
gridInfoFile = args[4]

## lat/lon values of first entries
xfirst = 0.  + ( xinc / 2. )
yfirst = 90. - ( yinc / 2. )

## dimensions of grid in number of pixels
xsize = 360. / xinc
ysize = 180. / yinc
gridsize = xsize * ysize

## open connection to output text file
fileConn = file( gridInfoFile )

## write data
writeLines( c(
    "gridtype        = lonlat",
    paste("gridsize  = ", gridsize, sep=""),
    "xname           = lon",
    "xlongname       = longitude",
    "xunits          = degrees_east",
    "yname           = lat",
    "ylongname       = latitude",
    "yunits          = degrees_north",
    paste("xsize     = ", xsize, sep=""),
    paste("ysize     = ", ysize, sep=""),
    paste("xfirst    = ", xfirst, sep=""),
    paste("xinc      = ", xinc, sep=""),
    paste("yfirst    = ", yfirst, sep=""),
    paste("yinc      = ", -yinc, sep="")
),
fileConn )

## close connection
close( fileConn )
