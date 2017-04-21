#!/usr/bin/env python2.7

import os
import sys
import argparse
import datetime

from pycmsaf.argparser import str2date
from config_suite import mysuite
from housekeeping import build_suite, str2upper
from pycmsaf.logger import setup_root_logger

logger = setup_root_logger(name='root')


def help():

    min_opt = "{0} --start_date <yyyymmdd> --end_date <yyyymmdd>".\
            format(os.path.basename(__file__))

    print "\n"
    logger.info(" *** Usage ***")
    logger.info("     ./{0}".format(min_opt))
    logger.info("     (a)   --dummy_case")
    logger.info("     (b)   --test_run")
    logger.info("     (c)   --satellites noaa18 terra metopa")
    logger.info("     (d)   --ignore_sats noaa18 terra metopa")
    logger.info("     (e)   --use_avhrr_primes [--ignore_sats terra aqua]")
    logger.info("     (f)   --use_modis_only")
    logger.info("     (g)   --proc_toa")
    logger.info("     (h)   --proc_day")
    logger.info("     (i)   --check_ECFS")
    logger.info(" *** TRY for more information")
    logger.info("     ./{0} --help".format(os.path.basename(__file__)))
    print "\n"
    sys.exit(0)
    

def datestring(dstr):
    """
    Convert date string containing '-' or '_' or '/'
    into date string without any character.
    """
    if '-' in dstr:
        correct_date_string = string.replace(dstr, '-', '')
    elif '_' in dstr:
        correct_date_string = string.replace(dstr, '_', '')
    elif '/' in dstr:
        correct_date_string = string.replace(dstr, '/', '')
    else:
        correct_date_string = dstr

    return correct_date_string


def str2mydate(dstring): 
    """
    Return datetime object.
    """
    dstr = datestring(dstring)
    if len(dstr) == 6:
        year = int(dstr[:-2])
        month = int(dstr[4:])
        return datetime.date(year, month, 1)
    else:
        logger.info("Possible formats: 2008-01, 2008/01, 2008_01, 200801")
        sys.exit(0)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description=u"{0} creates the suite {1} "
                    u"required by ecflow.".format(sys.argv[0], mysuite))

    parser.add_argument('--start_date', type=str2date, required=True,
                        help='First date of processing, e.g. 20090101')

    parser.add_argument('--end_date', type=str2date, required=True,
                        help='Last date of proecessing, e.g. 20091231')

    parser.add_argument('--satellites', type=str2upper, nargs='*',
                        help="List of satellites, which should be processed.")

    parser.add_argument('--ignore_sats', type=str2upper, nargs='*',
                        help="List of satellites which should be ignored.")

    #parser.add_argument('--ignore_months', type=str2mydate, nargs='*',
    #                    help="Ignore given yearmonth's, <yyyymm>" 
    #                          " e.g. 200201, 2002/03, 2002-04, 2002_09.")

    parser.add_argument('--ignore_months', type=int, nargs='*',
                        help="Ignore given month's, <mm>" 
                              " e.g. 1 2 5 7 11 12")

    parser.add_argument('--use_avhrr_primes', action="store_true",
                        help="Process only PRIME AVHRRs "
                             "if more AVHRRs are available.")

    parser.add_argument('--use_modis_only', action="store_true",
                        help="Process only MODIS.")

    parser.add_argument('--proc_day', type=int, default=-1,
                        help="Process only this day for given month "
                             "instead of whole month!")

    parser.add_argument('--test_run', action="store_true",
                        help="Run a subset of pixels")

    parser.add_argument('--dummy_run', action="store_true",
                        help="Dummy run, i.e. randomsleep only")

    parser.add_argument('--proc_toa', action="store_true",
                        help="Process L2 TOA variables and propagate into L3")
    
    parser.add_argument('--check_ECFS', action="store_true",
                        help="Check in ECFS archive whether L3 data already exist.")

    args = parser.parse_args()

    # -- dummy or test run
    if args.dummy_run and args.test_run:
        logger.info("Either choose --dummy_run or --test_run!")
        help()

    if args.dummy_run:
        dummycase = 1
        dummymess = "Only randomsleep commands will be executed."
    else:
        dummycase = 0
        dummymess = "Real processing will be executed."

    if args.test_run:
        testcase = 1
        message = "Note: Only 11x11 pixels of each orbit are being processed."
    else:
        testcase = 0
        message = "Note: Full orbits are being processed."

    if args.proc_toa:
        toacase = 1
        toamessage = "Processing and propagating TOA fluxes"
    else:
        toacase = 0
        toamessage = "TOA fluxes not processed"

    if args.check_ECFS:
        checkECFScase = True
        ECFSmessage = "Note: Only processing months with no L3 data in ECFS."
    else:
        checkECFScase = False
        ECFSmessage = "Note: Ignoring L3 data in ECFS - processing all months."        

    # -- either one specific day or whole month
    if args.proc_day != -1:
        
        diff = args.end_date.month - args.start_date.month

        if diff > 1:
            logger.info("""If you want to process a single day, then you can
            choose only 1 specific month!""")
            sys.exit(0)
        else:
            proc_year = args.start_date.year
            proc_month = args.start_date.month
            pday = datetime.date(proc_year, proc_month, args.proc_day)
            proc_day_message = "Only {0} will be processed".format(pday)

    else:
        proc_day_message = "Whole month will be processed"
    
    # -- either choose or ignore satellites
    if args.satellites and args.ignore_sats:
        logger.info("Options --satellites AND --ignore_sats not combinable!")
        help()

    # -- modis only option not combinable
    if args.use_modis_only:
        if args.satellites or args.ignore_sats or args.use_avhrr_primes:
            logger.info("Option USE MODIS ONLY not combinable!")
            help()

    # -- some screen output
    logger.info("SCRIPT \'{0}\' started\n".format(os.path.basename(__file__)))
    logger.info("START DATE    : {0}".format(args.start_date))
    logger.info("END DATE      : {0}".format(args.end_date))
    if args.satellites:
        logger.info("SATELLITES    : {0} will be processed".format(args.satellites))
    else:
        logger.info("SATELLITES    : take all (archive based)")
    logger.info("AVHRR PRIMES  : {0}".format(args.use_avhrr_primes))
    logger.info("MODIS ONLY    : {0}".format(args.use_modis_only))
    logger.info("IGNORE SATS   : {0}".format(args.ignore_sats))
    logger.info("IGNORE MONTHS : {0}".format(args.ignore_months))
    logger.info("PROC TOA      : {0} ({1})\n".format(args.proc_toa, toamessage))
    logger.info("PROC STATUS   : {0}".format(proc_day_message))
    if args.dummy_run: 
        logger.info("DUMMY RUN     : {0} ({1})\n".format(dummycase, dummymess))
    else: 
        logger.info("TESTCASE RUN  : {0} ({1})\n".format(testcase, message))
    if args.check_ECFS:
        logger.info("CHECKING ECFS : {0} ({1})\n".format(checkECFScase, ECFSmessage))

    build_suite(args.start_date, args.end_date,
                args.satellites, args.ignore_sats, args.ignore_months,
                args.use_avhrr_primes, args.use_modis_only,
                args.proc_day, dummycase, testcase, toacase, checkECFScase)

    logger.info("SCRIPT \'{0}\' finished\n".format(os.path.basename(__file__)))
