#!/usr/bin/env python2.7
from pycmsaf.logger import setup_root_logger
logger = setup_root_logger(name='root')

import os, sys
import ecflow
import argparse
import datetime
from dateutil.rrule import rrule, MONTHLY
from config_suite import *
from pycmsaf.avhrr_gac.database import AvhrrGacDatabase
from pycmsaf.argparser import str2date
from pycmsaf.utilities import date_from_year_doy
from pycmsaf.ssh_client import SSHClient

# ----------------------------------------------------------------
def str2upper(string_object): 
    return string_object.upper()


# ----------------------------------------------------------------
def enddate_of_month( year, month ):
    """
    Returns date of end of month.
    """
    last_days = [31, 30, 29, 28, 27]
    for i in last_days:
        try:
            end = datetime.datetime(year, month, i)
        except ValueError:
            continue
        else:
            return end.date()

    return None


# ----------------------------------------------------------------
def get_modis_avail( sat, sd, ed ):
    """
    Returns True or False for MODIS availability.
    """
    modis_dict = get_modis_dict()

    for sat_key in modis_dict:
        if sat_key == sat:
            for dat_key in modis_dict[sat_key]:
                if dat_key == "start_date":
                    msd = modis_dict[sat_key][dat_key]
                else:
                    med = modis_dict[sat_key][dat_key]

            # modis lies between user start and end date
            if sd >= msd and ed <= med:
                return True
            # modis lies partly between start and end date
            elif msd < sd < med:
                return True
            elif msd < ed < med:
                return True

    return False


# ----------------------------------------------------------------
def get_modis_list( user_sd, user_ed ):
    """
    Returns a list of modis satellites if available.
    """
    modis_list = list()

    modis_dict = get_modis_dict()

    for sat_key in modis_dict:
        for dat_key in modis_dict[sat_key]:

            if dat_key == "start_date":
                msd = modis_dict[sat_key][dat_key]
            else:
                med = modis_dict[sat_key][dat_key]

        # modis lies between user start and end date
        if user_sd >= msd and user_ed <= med:
            modis_list.append( sat_key )
        # modis lies partly between start and end date
        elif msd < user_sd < med:
            modis_list.append( sat_key )
        elif msd < user_ed < med:
            modis_list.append( sat_key )

    return modis_list


# ----------------------------------------------------------------
def get_modis_dict():
    """
    MODIS dictionary containing start and end dates of archive.
    """
    modis_dict = dict()

    for sat in ("TERRA", "AQUA"):
        modis_dict[sat] = dict()
        for dt in ("start_date", "end_date"):
            modis_dict[sat][dt] = 0

    modis_dict["TERRA"]["start_date"] = datetime.date(2000, 2, 24)
    modis_dict["TERRA"]["end_date"]   = datetime.date(2012, 12, 31)
    modis_dict["AQUA"]["start_date"]  = datetime.date(2002, 7, 4)
    modis_dict["AQUA"]["end_date"]    = datetime.date(2012, 12, 31)

    return modis_dict


# ----------------------------------------------------------------
def get_sensor(satellite):
    """
    Return sensor for given satellite.
    """

    if satellite == "TERRA" or satellite == "AQUA":
        sensor = "MODIS"
    elif satellite.startswith("NOAA") or \
         satellite.startswith("METOP"):
        sensor = "AVHRR"
    else:
        print " ! I do not know this satellite!\n"
        exit(0)

    return sensor

# ----------------------------------------------------------------
def set_vars(suite):
    """
    Set suite level variables
    """
    #suite.add_variable('TURTLES', 'I like turtles')
    suite.add_variable("ECF_MICRO", "%")

    # Specify the python interpreter to be used:
    suite.add_variable("PYTHON", \
            "PYTHONPATH=$PYTHONPATH:"+perm+" "+python_path)
    
    # Directory on the remote machine, where all generated 
    # files from "ECF_HOME" will be copied before execution
    #suite.add_variable("REMOTE_HOME", remote_home_dir)
    
    # Directory on the remote machine, 
    # where all jobs write their output
    suite.add_variable("REMOTE_LOGDIR", remote_log_dir)

    # Remote user and host names
    suite.add_variable("REMOTE_USER", remote_user_name)
    suite.add_variable("REMOTE_HOST", remote_host_name)
    
    # Standard ecflow variables:
    suite.add_variable("ECF_HOME", ecf_home_dir)
    suite.add_variable("ECF_FILES", ecf_files_dir)
    suite.add_variable("ECF_INCLUDE", ecf_include_dir)
    suite.add_variable("ECF_OUT", ecf_out_dir)
    # default value
    suite.add_variable("EC_TOTAL_SLAVES", 1)
    
    # Miscellaneous:
    suite.add_variable("ECF_TRIES", '1')
    suite.add_variable("ECF_SUBMIT", ecflow_submit)
    suite.add_variable("MAKE_CFG_FILE", make_cfg_files)
    suite.add_variable("COUNT_ORBIT_FILES", count_orbit_files)
    suite.add_variable("CLEANUP_SCRATCH", cleanup_scratch)
    suite.add_variable("ARCHIVE_DATA", archive_data)
    suite.add_variable("ECFS_L3_DIR", ecfs_l3_dir)
    suite.add_variable("ECFS_L2_DIR", ecfs_l2_dir)
    suite.add_variable("LD_LIB_PATH", ld_lib_path)
    suite.add_variable("TESTRUN", testcase)
    suite.add_variable("DUMMYRUN", dummycase)

    # some processing directories
    suite.add_variable("ESA_ROUTINE", esa_routine)
    suite.add_variable("ESA_OUTPUTDIR", esa_outputdir)
    suite.add_variable("ESA_LEVEL3DIR", esa_level3dir)
    suite.add_variable("ESA_INPUTDIR", esa_inputdir)
    suite.add_variable("ESA_LOGDIR", esa_logdir)

    # Config files
    suite.add_variable("CFG_PATHS_FILE", cfg_paths_file)
    suite.add_variable("CFG_ATTRI_FILE", cfg_attri_file)
    suite.add_variable("CFG_P1_AVHRR", cfg_pro1_avhrr)
    suite.add_variable("CFG_P1_MODIS", cfg_pro1_modis)
    suite.add_variable("CFG_P1_MARS", cfg_pro1_mars)
    suite.add_variable("CFG_P1_AUX", cfg_pro1_aux)
    suite.add_variable("CFG_P2_ORAC", cfg_pro2_orac)
    suite.add_variable("CFG_L3U_FILE", cfg_lev3u_file)
    suite.add_variable("CFG_L3C_FILE", cfg_lev3c_file)

    # ksh scripts
    suite.add_variable("GET_AVHRR_KSH", get_avhrr_ksh)
    suite.add_variable("GET_MODIS_KSH", get_modis_ksh)
    suite.add_variable("GET_MARS_KSH", get_mars_ksh)
    suite.add_variable("GET_AUX_KSH", get_aux_ksh)
    suite.add_variable("PROC2_ORAC_KSH", proc2_orac_ksh)
    suite.add_variable("SINGLE_DAY_KSH", single_day_ksh)
    suite.add_variable("RUN_L2TOL3_KSH", run_l2tol3_ksh)
    suite.add_variable("WRAPPER_EXE", wrapper_exe)

# ----------------------------------------------------------------
def add_fam(node, fam):
    """
    Make new family for given node.
    """
    new_fam = node.add_family( fam )
    return new_fam

# ----------------------------------------------------------------
def add_task(family, taskname):
    task = family.add_task(taskname)
    return task

# ----------------------------------------------------------------
def add_cleanup_aux_task(family, prefamily):
    cleanup_aux_data = add_task(family, 'cleanup_aux_data')
    add_trigger(cleanup_aux_data, prefamily)
    return dict(cleanup_aux_data=cleanup_aux_data)

# ----------------------------------------------------------------
def add_aux_tasks(family):
    wrt_aux_cfgs  = add_task(family, 'write_aux_cfg_files')
    get_aux_data  = add_task(family, 'get_aux_data')
    get_mars_data = add_task(family, 'get_mars_data')

    add_trigger(get_aux_data, wrt_aux_cfgs)
    add_trigger(get_mars_data, wrt_aux_cfgs)

    return dict(wrt_aux_cfgs=wrt_aux_cfgs,
                get_aux_data=get_aux_data,
                get_mars_data=get_mars_data)

# ----------------------------------------------------------------
def add_tasks(family, prefamily):
    wrt_main_cfgs   = add_task(family, 'write_main_cfg_files')
    get_sat_data    = add_task(family, 'get_sat_data')
    set_cpu_number  = add_task(family, 'set_cpu_number')
    retrieval       = add_task(family, 'retrieval')
    cleanup_l1_data = add_task(family, 'cleanup_l1_data')
    make_l3u_data   = add_task(family, 'make_l3u_daily_composites')
    make_l3c_data   = add_task(family, 'make_l3c_monthly_averages')
    archive_data    = add_task(family, 'archive_data')
    cleanup_l2_data = add_task(family, 'cleanup_l2_data')
    cleanup_l3_data = add_task(family, 'cleanup_l3_data')

    add_trigger(wrt_main_cfgs, prefamily)
    add_trigger(get_sat_data, wrt_main_cfgs)
    add_trigger(set_cpu_number, get_sat_data)
    add_trigger(retrieval, set_cpu_number)
    add_trigger(cleanup_l1_data, retrieval)
    add_trigger(make_l3u_data, cleanup_l1_data)
    add_trigger(make_l3c_data, cleanup_l1_data)
    add_trigger_expr(archive_data, 
                     make_l3u_data, make_l3c_data)
    add_trigger(cleanup_l2_data, archive_data)
    add_trigger(cleanup_l3_data, archive_data)

    return dict(wrt_main_cfgs=wrt_main_cfgs,
                get_sat_data=get_sat_data,
                set_cpu_number=set_cpu_number,
                retrieval=retrieval,
                cleanup_l1_data=cleanup_l1_data,
                make_l3u_data=make_l3u_data,
                make_l3c_data=make_l3c_data,
                archive_data=archive_data,
                cleanup_l2_data=cleanup_l2_data,
                cleanup_l3_data=cleanup_l3_data
               )

# ----------------------------------------------------------------
def add_trigger_expr(node, trigger1, trigger2):
    big_expr = ecflow.Expression( ecflow.PartExpression(
                '{0} == complete and {1} == complete'.format(
                 trigger1.get_abs_node_path(),
                 trigger2.get_abs_node_path()) ) )
    node.add_trigger( big_expr )

# ----------------------------------------------------------------
def add_trigger(node, trigger):
    """
    Make a given node wait for the trigger node to complete.

    @param node: The node that has to wait.
    @param trigger: The trigger node.
    @type node: ecflow.[family/task]
    @type trigger: ecflow.[family/task]
    @return: None
    """
    node.add_trigger('{0} == complete'.
            format(trigger.get_abs_node_path()))

# ----------------------------------------------------------------
def familytree(node, tree=None):
    """
    Given an ecflow node, walk the tree in downward direction 
    and collect all families.

    @param node: The node to start from.
    @type node: ecflow.Node
    @return: All collected families
    @rtype: list
    """
    # Initialize tree on the first call
    if tree is None:
        tree = list()

    # Walk the current node's subnodes
    subnodes = node.nodes
    for subnode in subnodes:
        # Save node to the tree if its type is ecflow.Family
        if isinstance(subnode, ecflow.Family):
            abspath = subnode.get_abs_node_path()
            tree.append(abspath[1:])    # skip initial '/' because otherwise
                                        # os.path.join() doesn't join paths
                                        # correctly.

            # Call function recursively.
            familytree(subnode, tree)

    return tree

# ----------------------------------------------------------------
def build_suite():
    """
    Build the ecflow suite.
    """

    logger.info('Building suite.')

    # ========================
    # GENERAL SUITE PROPERTIES
    # ========================
    defs  = ecflow.Defs()
    suite = defs.add_suite( mysuite )

    # Set suite level variables
    set_vars(suite)
    
    # Set default status
    suite.add_defstatus(ecflow.DState.suspended)

    # Define thread limits
    suite.add_limit("serial_threads", serial_threads_number)
    suite.add_limit("parallel_threads", parallel_threads_number)

    # ========================
    # DEFINE TOP LEVEL FAMILY
    # ========================
    fam_proc = add_fam( suite, 'proc' )

    # Activate thread limits
    #fam_proc.add_inlimit('serial_threads')
    fam_proc.add_inlimit('parallel_threads')
    
    # Define job commands
    fam_proc.add_variable('ECF_JOB_CMD', serial_job_cmd)

    # connect to database and get_sats list
    db = AvhrrGacDatabase( dbfile=gacdb_file )

    # ignored satellites
    default_ignore_sats = ['TIROSN', 'NOAA6', 'NOAA8', 'NOAA10']

    if args.ignoresats:
        add_ignore_sats = args.ignoresats
        ignore_list = default_ignore_sats + add_ignore_sats
    else:
        ignore_list = default_ignore_sats


    # Create list of available satellites
    if args.satellites:
        all_list = args.satellites
        avh_list = all_list
        mod_list = ["AQUA", "TERRA"]

        # avhrr database sat list
        db_sat_list = db.get_sats( start_date=args.sdate, 
                end_date=args.edate, ignore_sats=ignore_list)

        # update avhrr list (remove sat. with no data)
        verified_list = list(set(db_sat_list) - set(avh_list))

        # terra/aqua at the end of list, if data avail.
        for item in mod_list: 
            if item in all_list: 
                check = get_modis_avail( item, 
                        args.sdate, args.edate )
                if check == True: 
                    verified_list.append(item)

        # get final sat_list: match between verified and user list
        sat_list = list(set(all_list).intersection(verified_list))

    else:
        # avhrr
        sat_list = db.get_sats( start_date=args.sdate, 
                end_date=args.edate, ignore_sats=ignore_list)
        # modis
        mod_list  = get_modis_list( args.sdate, args.edate )
        sat_list += mod_list


    if len(sat_list) == 0:
        print ("\n *** There are no data for %s - %s \n" % 
                (args.sdate, args.edate))
        db.close()
        sys.exit(0)


    # ===============================
    # DEFINE DYNAMIC FAMILIES & TASKS
    # ===============================

    # month counter
    month_cnt = 0

    # loop over months for given date range
    for mm in rrule(MONTHLY, dtstart=args.sdate, until=args.edate): 

        yearstr  = mm.strftime("%Y")
        monthstr = mm.strftime("%m")
        
        modis_flag = False
        avhrr_flag = False


        # ----------------------------------------------------
        # check if AVHRR or/and MODIS are avail.
        # ----------------------------------------------------
        for s in sat_list:

            sensor = get_sensor( s )

            if sensor == "AVHRR" and avhrr_flag == False: 

                days = db.get_days( sat=s, year=int(yearstr), 
                        month=int(monthstr) )

                if len(days) > 0: 
                    avhrr_flag = True

            if sensor == "MODIS" and modis_flag == False: 

                modsd = datetime.date( int(yearstr), int(monthstr), 1)
                moded = enddate_of_month( int(yearstr), int(monthstr) )
                modis_flag = get_modis_avail( s, modsd, moded )

        if avhrr_flag == False and modis_flag == False:
            continue


        # ----------------------------------------------------
        # There is data
        # ----------------------------------------------------

        try: 
            fam_year = add_fam( fam_proc, yearstr )
            fam_year.add_variable("START_YEAR", yearstr)
            fam_year.add_variable("END_YEAR", yearstr)
        except:
            pass

        fam_month = add_fam(fam_year, monthstr) 
        fam_month.add_variable("START_MONTH", monthstr)
        fam_month.add_variable("END_MONTH", monthstr)


        # ----------------------------------------------------
        # add get aux/era family
        # ----------------------------------------------------
        fam_aux = add_fam( fam_month, "GET_AUX_DATA" )
        add_aux_tasks( fam_aux )

        # trigger for next month node
        if month_cnt > 0 :
            add_trigger( fam_aux, fam_month_previous )


        # ----------------------------------------------------
        # add family for satellite processing in general
        # ----------------------------------------------------
        fam_main = add_fam( fam_month, "MAIN_PROC" )

        # check if any ahvrr is available
        if avhrr_flag == True:
            fam_avhrr = add_fam( fam_main, "AVHRR" )
            fam_avhrr.add_variable("SENSOR", "AVHRR")

        # check if any modis is available
        if modis_flag == True:
            fam_modis = add_fam( fam_main, "MODIS" )
            fam_modis.add_variable("SENSOR", "MODIS")


        # process avail. satellites
        for counter, satellite in enumerate( sat_list ): 

            sensor = get_sensor( satellite )

            if sensor == "AVHRR":

                days = db.get_days( sat=satellite, 
                            year=int(yearstr), 
                            month=int(monthstr) )

                if len( days ) == 0: 
                    continue

                fam_sat = add_fam( fam_avhrr, satellite )
                fam_sat.add_variable( "SATELLITE", satellite )
                add_tasks( fam_sat, fam_aux )

            else:

                msdate = datetime.date( int(yearstr), int(monthstr), 1)
                medate = enddate_of_month( int(yearstr), int(monthstr) )
                mcheck = get_modis_avail( satellite, msdate, medate )

                if mcheck == False:
                    continue

                fam_sat = add_fam( fam_modis, satellite )
                fam_sat.add_variable( "SATELLITE", satellite )
                if avhrr_flag == True: 
                    add_tasks( fam_sat, fam_avhrr )
                else:
                    add_tasks( fam_sat, fam_aux )


        # ----------------------------------------------------
        # add cleanup aux/era family
        # ----------------------------------------------------
        fam_cleanup_aux = add_fam( fam_month, "CLEANUP_AUX_DATA" )
        add_cleanup_aux_task( fam_cleanup_aux, fam_main )

        # remember fam_month
        fam_month_previous = fam_month
        month_cnt += 1


    # close connection to database
    db.close()
    
    
    # ============================
    # CREATE SUITE DEFINITION FILE
    # ============================

    # Check job creation
    print defs.check_job_creation()

    # Save suite to file
    suite_def_file = mysuite + '.def'
    logger.info('Saving suite definition to file: {0}'.format(
                suite_def_file))
    defs.save_as_defs(suite_def_file)

    # ======================
    # CREATE LOG DIRECTORIES
    # ======================
    logger.info('Creating log directories on both the local and '
                'the remote machine.')

    # Create a tree of all families in the suite 
    # (i.e. families, subfamilies, subsubfamilies etc)
    tree = familytree(suite)

    # Create corresponding log-directory tree:
    # 1.) Local machine
    for node in tree:
        dirname = os.path.join(ecf_out_dir, node)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

    # 2.) Remote machine
    ssh = SSHClient(user=remote_user_name, host=remote_host_name)
    for node in tree:
        remote_dir = os.path.join(remote_log_dir, node)
        ssh.mkdir(remote_dir, batch=True)   # batch=True appends this mkdir
                                            # call to the command batch.

    # Create all remote directories in one step (is much faster)
    ssh.execute_batch()
# ----------------------------------------------------------------

# end of defs
# start of main code

# ================================================================

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=sys.argv[0]+'''
    creates the suite '''+mysuite+''' required by ecflow.''')
    
    parser.add_argument('--sdate', type=str2date, required=True,
            help='start date, e.g. 20090101')
    parser.add_argument('--edate', type=str2date, required=True,
            help='end date, e.g. 20091231')
    parser.add_argument( '--satellites', type=str2upper, nargs='*', 
            help='''List of satellites, which should be processed.''')
    parser.add_argument('--ignoresats', type=str2upper, nargs='*',
            help='''List of satellites which should be ignored.''')
    parser.add_argument('--testrun', 
            help='Run a subset of pixels', action="store_true")
    parser.add_argument('--dummy', 
            help='Dummy run, i.e. randomsleep only', action="store_true")
    
    args = parser.parse_args()


    if args.dummy == True:
        dummycase = 1
        dummymess = "Only randomsleep commands will be executed."
    else:
        dummycase = 0
        dummymess = "Real processing will be executed."


    if args.testrun == True:
        testcase = 1
        message = '''Note: Only 11x11 pixels of each orbit are being processed.''' 
    else:
        testcase = 0
        message = '''Note: Full orbits are being processed.'''


    if args.satellites and args.ignoresats:
        print ("""\n *** Either choose some satellites from list
                or ignore some satellites from list.\n\n
                *** Third option: neither use --satellites nor --ignoresats, 
                which means you will get all satellites that are available.\n""")
        sys.exit(0)


    print "\n"
    print (" * Script %s started " % sys.argv[0])
    print (" * start date  : %s" % args.sdate)
    print (" * end date    : %s" % args.edate)
    if args.satellites: 
        print (" * satellites  : %s" % args.satellites)
    else:
        print (" * satellites  : take all (archive based)")
    print (" * ignore sats : %s" % args.ignoresats)
    print (" * dummycase   : %s (%s)" % (dummycase, dummymess))
    print (" * testcase    : %s (%s)" % (testcase, message))
    print "\n"

    build_suite()

# ================================================================
