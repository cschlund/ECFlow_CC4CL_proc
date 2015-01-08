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


If you want to process only a single day (or a few days) for a month and
satellite, then you have to modify in ./esa_routines/ the python tool
"create_config_files.py" and set 'sday' and 'eday' as you wish,
instead of 1 and 0 (i.e. whole month is being processed).


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
        modify templates if necessary, 
        i.e. email, wall clock time, memory, etc.; 
        safe them without .template ending

    clear directories if necessary
        ./cleanup_local.sh

    generate suite definition

        recommendation: 
            before you run the "real" jobs (CC4CL), 
            please test ECFlow_CC4CL_proc using the option "--dummy",
            in order to check if your settings are OK.

            ./create_suite.py --sdate 20080101 --edate 20081231 --satellite noaa18 --dummy

        if everything worked out, then you can try to run a 11x11 pixel box:
            ./create_suite.py --sdate 20080101 --edate 20081231 --satellite noaa18 --testrun

        if everything worked out, then you can do the hard work:
            ./create_suite.py --sdate 20080101 --edate 20081231 --satellite noaa18

    load suite
        ./load.sh

    open ecflowview GUI
        ecflowview &
    and resume suite

