# write taskfile for L3_mpmd.cmd job creating l2B_sum data

# individual log file for each CPU?
individual_logs = T

# read command arguments
args = commandArgs(trailingOnly = T)

# define jobID and ndays from argument list
jobID = args[2]
ndays = args[3]

# base path to all subsequent files
base_path = "/perm/ms/de/sf7/esa_cci_c_proc/routine/"

# names of script and config files, attached to base path
# i.e. fully qualified file paths
ksh_script = paste(base_path, "run_l2tol3_script.ksh", sep="")
config_attributes = paste(base_path, "config_attributes.file", sep="")
config_paths = paste(base_path, "config_paths.file", sep="")

# create vector containing MPMD task calls
tasks = 1:ndays

# create MPMD task call for each day
for (i in 1:ndays){

   # convert single digit days to double digits
   i_dd = as.character(i)
   i_dd = ifelse(nchar(i_dd) == 1, paste("0", i_dd, sep=""), i_dd)

   # build config file name
   config_file = paste(base_path, "config_L3_day", i_dd, "_", jobID, ".file",
   sep="")
   
   # build log file name
   log_file = paste(base_path, "log_L3_mpmd_day", i_dd, "_", jobID, ".txt",
   sep="")

   # concatenate elements to build task call
   tasks[i] = paste(ksh_script, " ", jobID, " ", config_attributes, " ",
      config_paths, " ", config_file, sep="")
   tasks[i] = ifelse(individual_logs, paste(tasks[i], " > ", log_file,
   sep=""), tasks[i])

}

# write tasks vector to text file
out_name = paste("MPMD_tasks_", jobID, ".txt", sep="")
write.table(tasks, file=out_name, quote=F, row.names=F, col.names=F)
