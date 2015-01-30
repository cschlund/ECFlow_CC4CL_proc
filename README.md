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

    change to your home directory
        cd $HOME

    create a new directory for ecflow log
        mkdir ecflow_logs_username

    check which server is available, i.e. which is NOT in the list
        netstat -lnptu |less
        netstat -lnptu |grep 35816

    start ecflow server
        ecflow_start.sh -p 35816 -d $HOME/ecflow_logs_username

    stop ecflow server, if you do not need it anymore!
        ecflow_stop.sh -p 35816

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

            ./create_suite.py --start_date 20080101 --end_date 20081231 --satellites noaa18 --dummy

        if everything worked out, then you can try to run a 11x11 pixel box:
            ./create_suite.py --start_date 20080101 --end_date 20081231 --satellites noaa18 --testrun

        if everything worked out, then you can do the hard work:
            ./create_suite.py --start_date 20080101 --end_date 20081231 --satellites noaa18


        possibilities, for example:

        (1) process all available satellites
            ./create_suite.py --start_date 20080101 --end_date 20081231

        (2) process only noaa18 and terra
            ./create_suite.py --start_date 20080101 --end_date 20081231 --satellites noaa18 terra

        (3) process all available satellites except noaa18 and terra
            ./create_suite.py --start_date 20080101 --end_date 20081231 --ignoresats noaa18 terra

        (4) process avhrr primes and modis satellites
            ./create_suite.py --start_date 20080101 --end_date 20081231 --use_avhrr_primes

        (5) process avhrr primes but not modis satellites
            ./create_suite.py --start_date 20080101 --end_date 20081231 --use_avhrr_primes --ignore_sats terra aqua

        (6) process only modis satellites
            ./create_suite.py --start_date 20080101 --end_date 20081231 --use_modis_only


    load suite
        ./load.sh

    open ecflowview GUI
        ecflowview &
    and resume suite

