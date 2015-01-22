#!/usr/bin/env python2.7
import sys
import argparse
from pycmsaf.argparser import str2date
from config_suite import mysuite
from housekeeping import build_suite, str2upper

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

    parser.add_argument('--testrun', action="store_true",
            help='Run a subset of pixels')

    parser.add_argument('--dummy', action="store_true",
            help='Dummy run, i.e. randomsleep only')
    
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
        print ('''\n *** Either choose some satellites from list (1) or '''
               '''ignore some satellites from list (2).\n''' 
               '''\n *** Third option: neither use --satellites nor --ignoresats, '''
               '''which means you will get all satellites that are available.\n''')
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


    build_suite(args.sdate, args.edate, args.satellites, 
            args.ignoresats, dummycase, testcase)


# ================================================================
