## R script for writing remapping taskfile

## read command arguments
args = commandArgs( trailingOnly = T )

era_dir          = args[2]
gridInfoFile     = args[3]
remapWeightsFile = args[4]
taskfile         = args[5]
remapScript      = args[6]

files = list.files( era_dir, pattern = "*00.grb", full.names=T )
nfiles = length( files )
tasks = 1:nfiles

for ( i in 1:nfiles ){
    call = paste(remapScript, files[i], gridInfoFile, remapWeightsFile, sep=" ")
    tasks[i] = call
}

## write tasks vector to text file
write.table(tasks, file = taskfile, quote=F, row.names=F, col.names=F)
