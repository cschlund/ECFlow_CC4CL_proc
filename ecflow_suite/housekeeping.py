#!/usr/bin/env python2.7

import sys
import ecflow
import datetime
import calendar
import logging
import subprocess
from config_suite import *
from dateutil.rrule import rrule, MONTHLY
from pycmsaf.avhrr_gac.database import AvhrrGacDatabase
from pycmsaf.ssh_client import SSHClient

logger = logging.getLogger('root')


def subprocess_cmd(command): 
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    return proc_stdout


def get_svn_version(svndir):
    """
    Read SVN version from orac repository.
    """
    cmd = ('cd '+svndir+'; svn info; cd -')
    res = subprocess_cmd(cmd)

    stdout_lines = res.split("\n")
    for line in stdout_lines:
        if "Revision:" in line:
            line_list = line.split()
            if len(line_list) == 2: 
                svn = line_list[1] 
                break
            else:
                logger.info("Check stdout! snv info!")
                sys.exit(0)

    logger.info("Current SVN version = {0}".format(svn))
    return svn


def str2upper(string_object):
    """
    Converts given string into upper case.
    :rtype : string
    """
    return string_object.upper()


def enddate_of_month(year, month):
    """
    Returns date of end of month.
    :rtype: datetime object
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


def get_modis_avail(sat, sd, ed):
    """
    Returns True or False for MODIS availability.
    :rtype: bool
    """
    global msd, med
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


def get_modis_list(user_sd, user_ed):
    """
    Returns a list of modis satellites if available.
    :rtype : List
    """
    modis_list = list()

    modis_dict = get_modis_dict()

    for sat_key in modis_dict:
        for dat_key in modis_dict[sat_key]:

            if dat_key == "start_date":
                mod_sd = modis_dict[sat_key][dat_key]
            else:
                mod_ed = modis_dict[sat_key][dat_key]

        # modis lies between user start and end date
        if user_sd >= mod_sd and user_ed <= mod_ed:
            modis_list.append(sat_key)
        # modis lies partly between start and end date
        elif mod_sd < user_sd < mod_ed:
            modis_list.append(sat_key)
        elif mod_sd < user_ed < mod_ed:
            modis_list.append(sat_key)

    return modis_list


def get_avhrr_list():
    """
    Returns a list of avhrr satellites.
    :rtype: list
    """
    avhrr_list = ['NOAA7', 'NOAA9', 'NOAA11', 'NOAA12',
                  'NOAA14', 'NOAA15', 'NOAA16', 'NOAA17',
                  'NOAA18', 'NOAA19', 'METOPA', 'METOPB']
    return avhrr_list


def get_avhrr_prime_dict():
    """
    Returns a dictionary containing ahvrr prime information.
    ec_time    = equator crossing time
    start_date = Start of operational date.
    end_date   = End of operational date or new sat. in orbit.
    :rtype: dictionary
    """
    avhrr_dict = dict()
    avhrr_list = get_avhrr_list()
    attri_list = ["ec_time", "start_date", "end_date"]

    am_sats_list = ["NOAA12", "NOAA15", "NOAA17",
                    "METOPA", "METOPB"]

    # initialize dictionary
    for s in avhrr_list:
        avhrr_dict[s] = dict()
        for i in attri_list:
            avhrr_dict[s][i] = 0

    # fill dictionary
    for s in avhrr_list:
        for i in attri_list:
            if i == "ec_time":
                if s in am_sats_list:
                    avhrr_dict[s][i] = "AM"
                else:
                    avhrr_dict[s][i] = "PM"

    # --------------------------------------------------------------------
    avhrr_dict["NOAA7"]["start_date"] = datetime.date(1982, 1, 1)
    avhrr_dict["NOAA7"]["end_date"] = datetime.date(1985, 2, 1)
    # --------------------------------------------------------------------
    avhrr_dict["NOAA9"]["start_date"] = datetime.date(1985, 2, 25)
    avhrr_dict["NOAA9"]["end_date"] = datetime.date(1988, 11, 7)
    # --------------------------------------------------------------------
    avhrr_dict["NOAA11"]["start_date"] = datetime.date(1988, 11, 8)
    avhrr_dict["NOAA11"]["end_date"] = datetime.date(1994, 10, 16)
    # --------------------------------------------------------------------
    avhrr_dict["NOAA12"]["start_date"] = datetime.date(1991, 9, 17)
    avhrr_dict["NOAA12"]["end_date"] = datetime.date(1998, 12, 31)  # ->n15
    # --------------------------------------------------------------------
    avhrr_dict["NOAA14"]["start_date"] = datetime.date(1995, 4, 10)
    avhrr_dict["NOAA14"]["end_date"] = datetime.date(2001, 3, 31)  # ->n16
    # --------------------------------------------------------------------
    avhrr_dict["NOAA15"]["start_date"] = datetime.date(1999, 1, 1)
    avhrr_dict["NOAA15"]["end_date"] = datetime.date(2002, 10, 31)  # ->n17
    # --------------------------------------------------------------------
    avhrr_dict["NOAA16"]["start_date"] = datetime.date(2001, 4, 1)
    avhrr_dict["NOAA16"]["end_date"] = datetime.date(2005, 8, 31)  # ->n18
    # --------------------------------------------------------------------
    avhrr_dict["NOAA17"]["start_date"] = datetime.date(2002, 11, 1)
    avhrr_dict["NOAA17"]["end_date"] = datetime.date(2007, 5, 31)  # ->m02
    # --------------------------------------------------------------------
    avhrr_dict["NOAA18"]["start_date"] = datetime.date(2005, 9, 1)
    avhrr_dict["NOAA18"]["end_date"] = datetime.date(2009, 6, 30)  # ->n19
    # --------------------------------------------------------------------
    avhrr_dict["NOAA19"]["start_date"] = datetime.date(2009, 7, 1)
    avhrr_dict["NOAA19"]["end_date"] = datetime.date(2014, 12, 31)
    # --------------------------------------------------------------------
    avhrr_dict["METOPA"]["start_date"] = datetime.date(2007, 6, 1)
    avhrr_dict["METOPA"]["end_date"] = datetime.date(2013, 4, 30)  # ->m01
    # --------------------------------------------------------------------
    avhrr_dict["METOPB"]["start_date"] = datetime.date(2013, 5, 1)
    avhrr_dict["METOPB"]["end_date"] = datetime.date(2014, 12, 31)
    # --------------------------------------------------------------------

    return avhrr_dict


def get_modis_dict():
    """
    MODIS dictionary containing start and end dates of archive.
    :rtype: dictionary
    """
    modis_dict = dict()

    for sat in ("TERRA", "AQUA"):
        modis_dict[sat] = dict()
        for dt in ("start_date", "end_date"):
            modis_dict[sat][dt] = 0

    modis_dict["TERRA"]["start_date"] = datetime.date(2000, 2, 24)
    modis_dict["TERRA"]["end_date"] = datetime.date(2012, 12, 31)
    modis_dict["AQUA"]["start_date"] = datetime.date(2002, 7, 4)
    modis_dict["AQUA"]["end_date"] = datetime.date(2012, 12, 31)

    return modis_dict


def get_sensor(satellite):
    """
    Return sensor for given satellite.
    :rtype: string
    """

    global sensor
    if satellite == "TERRA" or satellite == "AQUA":
        sensor = "MODIS"
    elif satellite.startswith("NOAA") or \
            satellite.startswith("METOP"):
        sensor = "AVHRR"
    else:
        logger.info(" *** I do not know this satellite ***")
        exit(0)

    return sensor


def set_vars(suite, procday, dummycase, testcase, svn_version):
    """
    Set suite level variables
    :rtype: None
    """
    # suite.add_variable('TURTLES', 'I like turtles')
    suite.add_variable("ECF_MICRO", "%")

    # Specify the python interpreter to be used:
    suite.add_variable("PYTHON",
                       "PYTHONPATH=$PYTHONPATH:{0} {1}".format(perm,
                                                               python_path))

    # Directory on the remote machine, where all generated 
    # files from "ECF_HOME" will be copied before execution
    # suite.add_variable("REMOTE_HOME", remote_home_dir)

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
    suite.add_variable("SVN_VERSION", svn_version)
    suite.add_variable("ECF_TRIES", '1')
    suite.add_variable("ECF_SUBMIT", ecflow_submit)
    suite.add_variable("MAKE_CFG_FILE", make_cfg_files)
    suite.add_variable("COUNT_ORBIT_FILES", count_orbit_files)
    suite.add_variable("CLEANUP_SCRATCH", cleanup_scratch)
    suite.add_variable("ARCHIVE_DATA", archive_data)
    suite.add_variable("ECFS_L3_DIR", ecfs_l3_dir)
    suite.add_variable("ECFS_L2_DIR", ecfs_l2_dir)
    suite.add_variable("LD_LIB_PATH", ld_lib_path)
    suite.add_variable("PROCDAY", procday)
    suite.add_variable("TESTRUN", testcase)
    suite.add_variable("DUMMYRUN", dummycase)
    suite.add_variable("WRITE_MPMD_TASKFILE", write_mpmd_taskfile)
    suite.add_variable("WRITE_MPMD_CFGFILES", write_mpmd_cfgfiles)
    suite.add_variable("MPMD_SUBMITTER", mpmd_submitter)

    # some processing directories
    suite.add_variable("ESA_ROUTINE", esa_routine)
    suite.add_variable("ESA_OUTPUTDIR", esa_outputdir)
    suite.add_variable("ESA_LEVEL3DIR", esa_level3dir)
    suite.add_variable("ESA_INPUTDIR", esa_inputdir)
    suite.add_variable("ESA_LOGDIR", esa_logdir)
    suite.add_variable("ESA_CONFIGDIR", esa_configdir)
    suite.add_variable("ESA_LIST_L2FILES", esa_listl2files)
    suite.add_variable("ESA_ECF_LOG_DIR", esa_ecflogdir)

    # Config files
    suite.add_variable("CFG_PATHS_FILE", cfg_paths_file)
    suite.add_variable("CFG_ATTRI_FILE", cfg_attri_file)
    suite.add_variable("CFG_PREFIX", cfg_prefix)
    suite.add_variable("CFG_SUFFIX", cfg_suffix)

    # ksh scripts
    suite.add_variable("GET_AVHRR_KSH", get_avhrr_ksh)
    suite.add_variable("GET_MODIS_KSH", get_modis_ksh)
    suite.add_variable("GET_MARS_KSH", get_mars_ksh)
    suite.add_variable("GET_AUX_KSH", get_aux_ksh)
    suite.add_variable("PROC2_ORAC_KSH", proc2_orac_ksh)
    suite.add_variable("SINGLE_DAY_KSH", single_day_ksh)
    suite.add_variable("RUN_L2TOL3_KSH", run_l2tol3_ksh)
    suite.add_variable("WRAPPER_EXE", wrapper_exe)


def add_fam(node, fam):
    """
    Make new family for given node.
    """
    new_fam = node.add_family(fam)
    return new_fam


def add_task(family, taskname):
    """
    Adds the given task to the given family.
    """
    task = family.add_task(taskname)
    return task


def add_final_cleanup_task(family, prefamily):
    """
    Adds task for final cleanup of month.
    :rtype : dictionary
    """
    cleanup_l2_data = add_task(family, 'cleanup_l2_data')
    cleanup_l2bsum_files = add_task(family, 'cleanup_l2bsum_files')
    cleanup_aux_data = add_task(family, 'cleanup_aux_data')

    add_trigger(cleanup_l2_data, prefamily)
    add_trigger(cleanup_l2bsum_files, prefamily)
    add_trigger(cleanup_aux_data, prefamily)

    return {'cleanup_l2_data': cleanup_l2_data,
            'cleanup_l2bsum_files': cleanup_l2bsum_files,
            'cleanup_aux_data': cleanup_aux_data}


def add_aux_tasks(family):
    """
    Adds aux specific tasks to the given family.
    :rtype : dictionary
    """
    wrt_aux_cfgs = add_task(family, 'write_aux_cfg_files')
    get_aux_data = add_task(family, 'get_aux_data')
    get_mars_data = add_task(family, 'get_mars_data')

    add_trigger(get_aux_data, wrt_aux_cfgs)
    add_trigger(get_mars_data, wrt_aux_cfgs)

    return {'wrt_aux_cfgs': wrt_aux_cfgs,
            'get_aux_data': get_aux_data,
            'get_mars_data': get_mars_data}


def add_l3s_product_tasks(family, prefamily):
    """
    Adds tasks regarding L3S creation, final archiving,
    and cleanup l2 and l3 data.
    """
    make_l3s_data = add_task(family, 'make_l3s_sensorfam_monthly_averages')
    archive_l3s_data = add_task(family, 'archive_l3s_data')
    cleanup_l3s_data = add_task(family, 'cleanup_l3s_data')

    add_trigger(make_l3s_data, prefamily)
    add_trigger(archive_l3s_data, make_l3s_data)
    add_trigger(cleanup_l3s_data, archive_l3s_data)

    return {'make_l3s_data': make_l3s_data,
            'archive_l3s_data': archive_l3s_data,
            'cleanup_l3s_data': cleanup_l3s_data}


def add_main_proc_tasks(family, prefamily):
    """
    Adds main processing specific tasks to the given family.
    :rtype : dictionary
    """
    wrt_main_cfgs = add_task(family, 'write_main_cfg_files')
    get_sat_data = add_task(family, 'get_sat_data')
    set_cpu_number = add_task(family, 'set_cpu_number')
    retrieval = add_task(family, 'retrieval')
    cleanup_l1_data = add_task(family, 'cleanup_l1_data')
    archive_l2_data = add_task(family, 'archive_l2_data')
    prepare_l2b_sum = add_task(family, 'prepare_l2b_sum_files')
    make_l3u_data = add_task(family, 'make_l3u_daily_composites')
    archive_l3u_data = add_task(family, 'archive_l3u_data')
    cleanup_l3u_data = add_task(family, 'cleanup_l3u_data')
    make_l3c_data = add_task(family, 'make_l3c_monthly_averages')
    archive_l3c_data = add_task(family, 'archive_l3c_data')
    cleanup_l3c_data = add_task(family, 'cleanup_l3c_data')

    add_trigger(wrt_main_cfgs, prefamily)
    add_trigger(get_sat_data, wrt_main_cfgs)
    add_trigger(set_cpu_number, get_sat_data)
    add_trigger(retrieval, set_cpu_number)
    add_trigger(cleanup_l1_data, retrieval)
    add_trigger(archive_l2_data, retrieval)
    add_trigger(prepare_l2b_sum, cleanup_l1_data)
    add_trigger(make_l3u_data, cleanup_l1_data)
    add_trigger(archive_l3u_data, make_l3u_data)
    add_trigger(cleanup_l3u_data, archive_l3u_data)
    add_trigger(make_l3c_data, prepare_l2b_sum)
    add_trigger(archive_l3c_data, make_l3c_data)
    add_trigger(cleanup_l3c_data, archive_l3c_data)

    return {'wrt_main_cfgs': wrt_main_cfgs,
            'get_sat_data': get_sat_data,
            'set_cpu_number': set_cpu_number,
            'retrieval': retrieval,
            'cleanup_l1_data': cleanup_l1_data,
            'archive_l2_data': archive_l2_data,
            'prepare_l2b_sum': prepare_l2b_sum,
            'make_l3u_data': make_l3u_data,
            'archive_l3u_data': archive_l3u_data,
            'cleanup_l3u_data': cleanup_l3u_data,
            'make_l3c_data': make_l3c_data,
            'archive_l3c_data': archive_l3c_data,
            'cleanup_l3c_data': cleanup_l3c_data}


def add_trigger_expr(node, trigger1, trigger2):
    """
    Make a given node wait for both trigger nodes to complete.
    :rtype : None
    """
    big_expr = ecflow.Expression(ecflow.PartExpression(
        '{0} == complete and {1} == complete'.format(
            trigger1.get_abs_node_path(),
            trigger2.get_abs_node_path())))
    node.add_trigger(big_expr)


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
            tree.append(abspath[1:])  # skip initial '/' because otherwise
            # os.path.join() doesn't join paths
            # correctly.

            # Call function recursively.
            familytree(subnode, tree)

    return tree


def verify_avhrr_primes(sat_list, act_date):
    """
    Selects only prime AVHRRs from given satellite list for given date.
    :rtype : list
    """
    plist = list()
    pdict = get_avhrr_prime_dict()

    for s in sat_list:
        if s == "AQUA" or s == "TERRA":
            plist.append(s)
            continue
        if pdict[s]["start_date"] <= act_date <= pdict[s]["end_date"]:
            plist.append(s)

    return plist


def verify_satellite_settings(dbfile, sdate, edate, satellites_list,
                              ignoresats_list, modisonly):
    """
    Provides a list of available satellites based on the
    user specification and on databases.
    :rtype : list
    """

    # ignored satellites
    default_ignore_sats = ['TIROSN', 'NOAA6', 'NOAA8', 'NOAA10']
    if ignoresats_list:
        add_ignore_sats = ignoresats_list
        ignore_list = default_ignore_sats + add_ignore_sats
    else:
        ignore_list = default_ignore_sats

    # Create list of available satellites
    if satellites_list:
        all_list = satellites_list
        # noinspection PyUnusedLocal
        avh_list = all_list
        mod_list = ["AQUA", "TERRA"]

        # avhrr database sat list
        db_sat_list = dbfile.get_sats(start_date=sdate, end_date=edate,
                                      ignore_sats=ignore_list)

        # terra/aqua at the end of list, if data avail.
        for item in mod_list:
            if item in all_list:
                check = get_modis_avail(item, sdate, edate)
                if check:
                    db_sat_list.append(item)

        # get final sat_list: match between verified and user list
        sat_list = list(set(all_list).intersection(db_sat_list))

    # modis only
    elif modisonly is True:
        sat_list = get_modis_list(sdate, edate)

    # take all except ignore_sats
    else:
        # avhrr
        sat_list = dbfile.get_sats(start_date=sdate, end_date=edate,
                                   ignore_sats=ignore_list)
        # modis
        mod_list = get_modis_list(sdate, edate)
        sat_list += mod_list

        # check ignoresats
        for ml in mod_list:
            if ml in ignore_list:
                if ml in sat_list:
                    idx = sat_list.index(ml)
                    del sat_list[idx]


    # -- sort satellite list, MODIS last
    sort_avhrr_list = list()
    sort_modis_list = list()

    for s in sat_list:
        if s == "TERRA" or s == "AQUA":
            sort_modis_list.append(s)
        else:
            sort_avhrr_list.append(s)

    if len(sort_avhrr_list) > 0: 
        sort_avhrr_list.sort()
    if len(sort_modis_list) > 0: 
        sort_modis_list.sort()

    sorted_sat_list = sort_avhrr_list + sort_modis_list

    return sorted_sat_list


def build_suite(sdate, edate, satellites_list, ignoresats_list,
                ignoremonths_list, useprimes, modisonly, 
                procday, dummycase, testcase):
    """
    Build the ecflow suite.
    """

    global fam_month_previous, fam_avhrr, fam_modis, fam_year
    logger.info('Building suite.')

    # get SVN version
    svn_version = get_svn_version(svn_path)

    # ========================
    # GENERAL SUITE PROPERTIES
    # ========================
    defs = ecflow.Defs()
    suite = defs.add_suite(mysuite)

    # Set suite level variables
    set_vars(suite, procday, dummycase, testcase, svn_version)

    # Set default status
    suite.add_defstatus(ecflow.DState.suspended)

    # Define thread limits
    suite.add_limit("serial_threads", serial_threads_number)
    suite.add_limit("parallel_threads", parallel_threads_number)

    # ========================
    # DEFINE TOP LEVEL FAMILY
    # ========================
    fam_proc = add_fam(suite, big_fam)

    # Activate thread limits
    # fam_proc.add_inlimit('serial_threads')
    fam_proc.add_inlimit('parallel_threads')

    # Define job commands
    fam_proc.add_variable('ECF_JOB_CMD', serial_job_cmd)

    # connect to database and get_sats list
    db = AvhrrGacDatabase(dbfile=gacdb_file)

    # verify user input and database content
    logger.info('Verify satellite settings')
    sat_list = verify_satellite_settings(db, sdate, edate,
                                         satellites_list,
                                         ignoresats_list,
                                         modisonly)

    # Are there any data for processing?
    if len(sat_list) == 0:
        logger.info("--------------------------------------------------------")
        logger.info("*** There are no data for {0} - {1}".format(sdate, edate))
        logger.info("Please check parameters you have passed!")
        logger.info("--------------------------------------------------------")
        db.close()
        sys.exit(0)

    # ================================
    # DEFINE DYNAMIC FAMILIES & TASKS
    # ================================

    # memorize satellites for each month
    satellites_within_current_month = list()

    # relevant for post_proc: L3S
    avhrr_logdirs = list()
    modis_logdirs = list()
    l2bsum_logdirs_within_current_month = list()

    # month counter
    month_cnt = 0

    # ----------------------------------------------------
    # loop over months for given date range
    # ----------------------------------------------------
    for mm in rrule(MONTHLY, dtstart=sdate, until=edate):

        yearstr = mm.strftime("%Y")
        monthstr = mm.strftime("%m")
        act_date = datetime.date(int(yearstr), int(monthstr), 1)
        ndays_of_month = calendar.monthrange(int(yearstr), 
                                             int(monthstr))[1]

        # check if month should be skipped, if given
        if ignoremonths_list:
            # if act_date in ignoremonths_list:
            if int(monthstr) in ignoremonths_list:
                continue

        # check for avhrr primes
        if useprimes:
            sat_list = verify_avhrr_primes(sat_list,
                                           act_date)

        # check if any AVHRR or/and MODIS are avail.
        modis_flag = False
        avhrr_flag = False
        for s in sat_list:
            isensor = get_sensor(s)

            if isensor == "AVHRR" and avhrr_flag is False:
                days = db.get_days(sat=s, year=int(yearstr),
                                   month=int(monthstr))
                if len(days) > 0:
                    avhrr_flag = True

            if isensor == "MODIS" and modis_flag is False:
                modsd = datetime.date(int(yearstr), int(monthstr), 1)
                moded = enddate_of_month(int(yearstr), int(monthstr))
                modis_flag = get_modis_avail(s, modsd, moded)

        # neither avhrr nor modis -> go to next month
        if avhrr_flag is False and modis_flag is False:
            continue

        # there is data: add fam. year if not already existing
        try:
            fam_year = add_fam(fam_proc, yearstr)
            fam_year.add_variable("START_YEAR", yearstr)
            fam_year.add_variable("END_YEAR", yearstr)
        except RuntimeError:
            pass

        # add fam. month
        fam_month = add_fam(fam_year, monthstr)
        fam_month.add_variable("START_MONTH", monthstr)
        fam_month.add_variable("END_MONTH", monthstr)
        fam_month.add_variable("NDAYS_OF_MONTH", ndays_of_month)

        # add get aux/era family
        fam_aux = add_fam(fam_month, get_aux_fam)
        add_aux_tasks(fam_aux)

        # trigger for next month node
        if month_cnt > 0:
            add_trigger(fam_aux, fam_month_previous)

        # add fam. main processing
        fam_main = add_fam(fam_month, mainproc_fam)

        # if avhrr data available for current month
        if avhrr_flag:
            fam_avhrr = add_fam(fam_main, "AVHRR")
            fam_avhrr.add_variable("SENSOR", "AVHRR")

        # if modis data available for current month
        if modis_flag:
            fam_modis = add_fam(fam_main, "MODIS")
            fam_modis.add_variable("SENSOR", "MODIS")

        # process avail. satellites for current month
        for counter, satellite in enumerate(sat_list):
            isensor = get_sensor(satellite)

            if isensor == "AVHRR":
                days = db.get_days(sat=satellite,
                                   year=int(yearstr),
                                   month=int(monthstr))
                if len(days) == 0:
                    continue

                fam_sat = add_fam(fam_avhrr, satellite)
                fam_sat.add_variable("SATELLITE", satellite)
                add_main_proc_tasks(fam_sat, fam_aux)
                satellites_within_current_month.append(satellite)
                l2bsum_logdir = os.path.join(esa_ecflogdir, mysuite, 
                                             big_fam, yearstr, monthstr, 
                                             isensor, satellite)
                l2bsum_logdirs_within_current_month.append(l2bsum_logdir)
            else:
                msdate = datetime.date(int(yearstr), int(monthstr), 1)
                medate = enddate_of_month(int(yearstr), int(monthstr))
                mcheck = get_modis_avail(satellite, msdate, medate)

                if not mcheck:
                    continue

                fam_sat = add_fam(fam_modis, satellite)
                fam_sat.add_variable("SATELLITE", satellite)
                satellites_within_current_month.append(satellite)
                l2bsum_logdir = os.path.join(esa_ecflogdir, mysuite, 
                                             big_fam, yearstr, monthstr, 
                                             isensor, satellite)
                l2bsum_logdirs_within_current_month.append(l2bsum_logdir)

                if avhrr_flag:
                    add_main_proc_tasks(fam_sat, fam_avhrr)
                    fam_avhrr = fam_sat
                else:
                    add_main_proc_tasks(fam_sat, fam_aux)
                    fam_aux = fam_sat

        # -- end of satellite loop

        # satellites within current month
        logger.info("satellites_within_current_month:{0}".
                format(satellites_within_current_month))

        # check if enough satellites are available for L3S product
        avhrr_cnt = 0
        modis_cnt = 0

        for ldirs in l2bsum_logdirs_within_current_month:
            if "AVHRR" in ldirs:
                avhrr_cnt += 1
                avhrr_logdirs.append(ldirs)
            if "MODIS" in ldirs:
                modis_cnt += 1
                modis_logdirs.append(ldirs)

        # add fam. post processing
        if avhrr_cnt > 1 or modis_cnt > 1: 
            fam_post = add_fam(fam_month, postproc_fam)
            last_fam_trigger = fam_post
        else:
            last_fam_trigger = fam_main

        if avhrr_cnt > 1:
            fam_avhrr_post = add_fam(fam_post, "AVHRR_L3S")
            fam_avhrr_post.add_variable("SENSOR_FAM", "AVHRR")
            add_l3s_product_tasks(fam_avhrr_post, fam_main)
            fam_avhrr_post.add_variable('L2B_SUM_LOGDIRS', ' '.join(avhrr_logdirs))
            logger.info("L3S: {0} AVHRR(s) in {1} for {2}/{3}".
                        format(avhrr_cnt, mainproc_fam, yearstr, monthstr))
            logger.info("Use {0} for L3S production".format(avhrr_logdirs))
        else:
            logger.info("No L3S production due to "
                        "{0} AVHRR in {1} for {2}/{3}".
                        format(avhrr_cnt, mainproc_fam, yearstr, monthstr))

        if modis_cnt > 1:
            fam_modis_post = add_fam(fam_post, "MODIS_L3S")
            fam_modis_post.add_variable("SENSOR_FAM", "MODIS")
            add_l3s_product_tasks(fam_modis_post, fam_main)
            fam_modis_post.add_variable('L2B_SUM_LOGDIRS', ' '.join(modis_logdirs))
            logger.info("L3S: {0} MODIS(s) in {1} for {2}/{3}".
                        format(modis_cnt, mainproc_fam, yearstr, monthstr))
            logger.info("Use {0} for L3S production".format(modis_logdirs))
        else:
            logger.info("No L3S production due to "
                        "{0} MODIS in {1} for {2}/{3}".
                        format(modis_cnt, mainproc_fam, yearstr, monthstr))

        # add cleanup aux/era, l2, l2_sum files
        fam_final_cleanup = add_fam(fam_month, final_fam)
        fam_final_cleanup.add_variable('CURRENT_SATELLITE_LIST',
                ' '.join(satellites_within_current_month))
        add_final_cleanup_task(fam_final_cleanup, last_fam_trigger)

        # remember fam_month
        fam_month_previous = fam_month
        month_cnt += 1

        # reset lists
        satellites_within_current_month = []
        l2bsum_logdirs_within_current_month = []
        avhrr_logdirs = []
        modis_logdirs = []

    # ----------------------------------------------------
    # end of loop over months
    # ----------------------------------------------------

    # close connection to database
    db.close()

    # ============================
    # CREATE SUITE DEFINITION FILE
    # ============================

    # Check job creation
    logger.info("Defs Check Job Creation: {0}".
            format(defs.check_job_creation()))

    # Save suite to file
    suite_def_file = mysuite + '.def'
    logger.info('Saving suite definition to file: {0}'.format(suite_def_file))
    defs.save_as_defs(suite_def_file)

    # ======================
    # CREATE LOG DIRECTORIES
    # ======================
    logger.info('Creating log directories on both the '
            'local and the remote machine.\n')

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
        ssh.mkdir(remote_dir, batch=True)  # batch=True appends this mkdir
        # call to the command batch.

    # Create all remote directories in one step (is much faster)
    ssh.execute_batch()
