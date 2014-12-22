ECFlow_CC4CL_proc
=================

Cloud_cci CC4CL using ecflow

Dependencies: You need also to install

    https://github.com/Funkensieper/pycmsaf.git

    "AVHRR_GAC_archive.sqlite3": 
    original database must be located in your pycmsat install.dir.
    e.g. "/perm/ms/de/sf7/cschlund/pycmsaf/AVHRR_GAC_archive.sqlite3"

    
    additionally you need the main CC4CL source code, which is not
    included in this repository, e.g. "/path/to/cschlund/mainsrc"


You have to clone this repository twice:

    1) local machine, e.g. ecgate: /path/to/repo

    2) remote machine, eg.g cca: /path/to/repo


If you want to run only a small pixel box instead of the whole orbit, 
please create your suite using "--testrun"

    For more details: ./create_suite.py --help


./esa_routines/

    this is the source code, which is running on the remote machine;
        first modify "config_paths.file";
        then compile source code using "gmake"


./ecflow_suite/

    this is the source code for ecflow required on local machine

    start ecflow server
        ecflow_start.sh -p 3500 -d $HOME/ecflow_logs

    stop ecflow server, if you do not need it anymore!
        ecflow_stop.sh -p 3500

    edit config.sh
        adapt all variables and paths!

    check if ecflow server is running
        source config.sh
        ecflow_client --ping

    edit suite config file
        edit config_suite.py

    go to include/
        modify templates if necessary, i.e. email, wall clock time, memory, etc.; safe them without .template ending

    got to tasks/
        modify ecflow scripts; save them without .template ending;

        recommendation: 
            before you activate the real jobs in the scripts, 
            run ecflow with "randomsleep" job only, testing if your settings are OK.
            If everything worked out, then deactivate the randomsleep call and 
            activate the code below, which is deactivated by default.

    clear directories if necessary
        ./cleanup_local.sh
        ./cleanup_remote.sh

    generate suite definition
        ./create_suite.py --sdate 20080101 --edate 20081231
        ./create_suite.py --sdate 20080101 --edate 20081231 --satellite noaa18 --testrun

    load suite
        ./load.sh

    open ecflowview GUI
        ecflowview &
    and resume suite

