#!/usr/bin/env python2.7
import sys
import argparse, datetime
from pycmsaf.argparser import str2date
from config_suite import mysuite
from housekeeping import build_suite, str2upper

# ================================================================

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=sys.argv[0]+'''
    creates the suite '''+mysuite+''' required by ecflow.''')
    
    parser.add_argument('--start_date', type=str2date, required=True,
            help='First date of processing, e.g. 20090101')

    parser.add_argument('--end_date', type=str2date, required=True,
            help='Last date of proecessing, e.g. 20091231')

    parser.add_argument( '--satellites', type=str2upper, nargs='*', 
            help='''List of satellites, which should be processed.''')

    parser.add_argument('--ignore_sats', type=str2upper, nargs='*',
            help='''List of satellites which should be ignored.''')

    parser.add_argument('--use_avhrr_primes', action="store_true",
            help="Process only PRIME AVHRRs if more AVHRRs are available.")

    parser.add_argument('--use_modis_only', action="store_true",
            help="Process only MODIS.")

    parser.add_argument('--proc_day', type=int, default=-1,
            help="Process only this day for given month instead of whole month!")

    parser.add_argument('--test_run', action="store_true",
            help='Run a subset of pixels')

    parser.add_argument('--dummy_run', action="store_true",
            help='Dummy run, i.e. randomsleep only')
    
    args = parser.parse_args()


    if args.dummy_run == True:
        dummycase = 1
        dummymess = "Only randomsleep commands will be executed."
    else:
        dummycase = 0
        dummymess = "Real processing will be executed."


    if args.proc_day != -1:
        diff = args.end_date.month - args.start_date.month
        if diff > 1:
            print ("\n *** If you want to process a single day, "
                    "then you can choose only 1 specific month!\n")
            sys.exit(0)
        else:
            proc_year  = args.start_date.year
            proc_month = args.start_date.month
            pday = datetime.date( proc_year, proc_month, args.proc_day )
            proc_day_message = "Only {d} will be processed".\
                                format(d=pday)
    else: 
        proc_day_message = "Whole month will be processed"


    # help message
    min_opt = " --start_date <yyyymmdd> --end_date <yyyymmdd> "
    options = ( '''\n *** Usage information:\n'''
            '''     {s} [--test_run] [--dummy_case]\n'''
            '''     {s} --satellites noaa18 terra metopa\n'''
            '''     {s} --ignore_sats noaa18 terra metopa\n'''
            '''     {s} --use_avhrr_primes [--ignore_sats terra aqua]\n'''
            '''     {s} --use_modis_only \n''').format( s=min_opt )

    if args.test_run == True:
        testcase = 1
        message = '''Note: Only 11x11 pixels of each orbit are being processed.''' 
    else:
        testcase = 0
        message = '''Note: Full orbits are being processed.'''


    if args.satellites and args.ignore_sats:
        print ("\n *** Options --satellites AND --ignore_sats not combinable! ")
        print options
        sys.exit(0)


    if args.use_modis_only:
        if args.satellites or args.ignore_sats or args.use_avhrr_primes:
            print ("\n *** Option USE MODIS ONLY not combinable!")
            print options
            sys.exit(0)


    print "\n"
    print (" * Script %s started " % sys.argv[0])
    print (" * start date  : %s" % args.start_date)
    print (" * end date    : %s" % args.end_date)
    if args.satellites: 
        print (" * satellites  : %s" % args.satellites)
    else:
        print (" * satellites  : take all (archive based)")
    print (" * avhrr primes: %s" % args.use_avhrr_primes)
    print (" * modis only  : %s" % args.use_modis_only)
    print (" * ignore sats : %s" % args.ignore_sats)
    print (" * proc. status: %s" % proc_day_message)
    print (" * dummycase   : %s (%s)" % (dummycase, dummymess))
    print (" * testcase    : %s (%s)" % (testcase, message))
    print "\n"


    build_suite( args.start_date, args.end_date, 
                 args.satellites, args.ignore_sats, 
                 args.use_avhrr_primes, args.use_modis_only, 
                 args.proc_day, dummycase, testcase )


# ================================================================
