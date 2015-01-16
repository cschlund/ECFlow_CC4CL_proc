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
def get_modis_list():
    """
    MODIS data list
    """
    mlist = dict()
    for sat in ("TERRA", "AQUA"):
        mlist[sat] = dict()
        for dt in ("start_date", "end_date"):
            mlist[sat][dt] = 0

    mlist["TERRA"]["start_date"] = datetime.date(2000, 2, 24)
    mlist["TERRA"]["end_date"] = datetime.date(2012, 12, 31)
    mlist["AQUA"]["start_date"] = datetime.date(2002, 7, 4)
    mlist["AQUA"]["end_date"] = datetime.date(2012, 12, 31)

    return mlist

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


    # Create list of available satellites
    if args.satellite:
        sat_list = [args.satellite.upper()]
    else:
        # connect to database and get_sats list
        db = AvhrrGacDatabase( dbfile=gacdb_file )
        sat_list = db.get_sats( start_date=args.sdate, 
                                end_date=args.edate,
                                ignore_sats=['NOAA6', 'NOAA8',
                                    'NOAA10'])

        mod_list = get_modis_list()
        for key in mod_list:
            cnt = 0
            for key2 in mod_list[key]:
                if cnt == 0: 
                    msdt = mod_list[key][key2]
                if cnt == 1: 
                    medt = mod_list[key][key2]
                cnt =+ 1
            if args.sdate >= msdt and args.edate <= medt: 
                sat_list.append(key)


    # ===============================
    # DEFINE DYNAMIC FAMILIES & TASKS
    # ===============================

    # month counter
    month_cnt = 0

    # loop over months for given date range
    for mm in rrule(MONTHLY, dtstart=args.sdate, until=args.edate): 

        year_string  = mm.strftime("%Y")
        month_string = mm.strftime("%m")
        
        try: 
            fam_year = add_fam( fam_proc, year_string )
            fam_year.add_variable("START_YEAR", year_string)
            fam_year.add_variable("END_YEAR", year_string)
        except:
            pass

        fam_month = add_fam(fam_year, month_string) 
        fam_month.add_variable("START_MONTH", month_string)
        fam_month.add_variable("END_MONTH", month_string)


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
        fam_main = add_fam(fam_month, "MAIN_PROC")

        # process avail. satellites
        for counter, satellite in enumerate(sat_list): 

            # get sensor for satellite
            sensor = get_sensor(satellite)

            # add satellite and sensor families
            fam_instr = add_fam(fam_main, satellite+'_'+sensor)
            fam_instr.add_variable("SATELLITE", satellite)
            fam_instr.add_variable("SENSOR", sensor)

            # trigger for next satellite
            if counter > 0:
                add_trigger(fam_instr, fam_instr_previous)

            # remember previous sat_ins node
            fam_instr_previous = fam_instr

            # add tasks
            add_tasks( fam_instr, fam_aux )


        # ----------------------------------------------------
        # add cleanup aux/era family
        # ----------------------------------------------------
        fam_cleanup_aux = add_fam( fam_month, "CLEANUP_AUX_DATA" )
        add_cleanup_aux_task( fam_cleanup_aux, fam_main )

        # remember fam_month
        fam_month_previous = fam_month
        month_cnt += 1

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
    
    parser.add_argument('--sdate', type=str2date,
            help='start date, e.g. 20090101', required=True)
    parser.add_argument('--edate', type=str2date,
            help='end date, e.g. 20091231',required=True)
    parser.add_argument( '--satellite', type=str,
            help='''satellite name, e.g. noaa15, metopa, 
            terra, aqua''')
    parser.add_argument('--testrun',
            help='Run a subset of pixels', action="store_true")
    parser.add_argument('--dummy',
            help='Dummy run, i.e. randomsleep only', action="store_true")
    
    args = parser.parse_args()

    if args.dummy == True:
        dummycase = 1
    else:
        dummycase = 0

    if args.testrun == True:
        testcase = 1
        message = '''Note: Only 11x11 pixels of each orbit are being processed.\n''' 
    else:
        testcase = 0
        message = '''Note: Full orbits are being processed\n.'''


    print ("\n * Script %s started " % sys.argv[0])
    print (" * start date : %s" % args.sdate)
    print (" * end date   : %s" % args.edate)
    print (" * testcase   : %s (%s)" % (testcase, message))

    build_suite()

# ================================================================
