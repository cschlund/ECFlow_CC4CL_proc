#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#
# C.Schlundt: November, 2014
#

import os, sys
import argparse
from housekeeping import get_id
from housekeeping import split_platform_string
from housekeeping import tar_l3_results


# -------------------------------------------------------------------
# --- main ---
# -------------------------------------------------------------------
if __name__ == '__main__': 

    # -- parser arguments
    parser = argparse.ArgumentParser(description='''%s
    creates tar files for L3U and L3C. 
    The subroutines are defined in "housekeeping.py".
    ''' % (os.path.basename(__file__)))
    
    parser.add_argument('--inpdir', type=str, required=True, 
            help='String, e.g. /path/to/output/level3')
    parser.add_argument('--ecfsdir', type=str, required=True, 
            help='String, e.g. /ecfs/path/to/L3/data')
    parser.add_argument('--instrument', type=str, required=True, 
            help='String, e.g. AVHRR')
    parser.add_argument('--satellite', type=str,required=True, 
            help='String, e.g. NOAA18')
    parser.add_argument('--year', type=int, required=True, 
            help='Integer, e.g. 2008')
    parser.add_argument('--month', type=int, required=True, 
            help='Integer, e.g. 1')
    
    args = parser.parse_args()
    
    
    # -- make some screen output
    print ( " * %s started for %s/%s : %s/%s - %s! " 
             %( os.path.basename(__file__), args.instrument,
                args.satellite, args.year, args.month,
                args.inpdir) )
    
    
    # -- create date string
    datestring = str(args.year) + str('%02d' % args.month)
    
    
    # -- sensor and platform settings
    if args.instrument.upper() == "AVHRR": 
        (satstr, satnum) = split_platform_string( args.satellite )
        sensor = args.instrument.upper()
        platform = satstr.upper() + '-' + satnum
    else:
        sensor = args.instrument.upper() 
        platform  = args.satellite.upper()


    # -- list everything in input directory
    alldirs = os.listdir( args.inpdir )


    # *** L3C archiving ***

    # -- find latest job via ID-US number
    if len(alldirs) > 0:
        getdirs = list()
        # collect right subfolders
        for ad in alldirs:
            if datestring in ad \
                    and args.instrument.upper() in ad \
                    and args.satellite.upper() in ad \
                    and 'monthly_means' in ad:
                        getdirs.append( ad )
        # sort list
        getdirs.sort()
        # get last element from list, should be last job
        lastdir = getdirs.pop()
        # get ID number from the last job
        idnumber = get_id( lastdir )
        # archive data
        tar_l3_results( "L3C", args.inpdir, datestring, 
                        sensor, platform, idnumber, args.ecfsdir)
    else:
        print (" ! Check your input directory, maybe it is empty ? \n")

    
    # *** L3U archiving ***

    # -- find latest job via ID-US number
    if len(alldirs) > 0:
        getdirs = list()
        # collect right subfolders
        for ad in alldirs:
            if datestring in ad \
                    and args.instrument.upper() in ad \
                    and args.satellite.upper() in ad \
                    and 'daily_samples' in ad:
                        getdirs.append( ad )
        # sort list
        getdirs.sort()
        # get last element from list, should be last job
        lastdir = getdirs.pop()
        # get ID number from the last job
        idnumber = get_id( lastdir )
        # archive data
        tar_l3_results( "L3U", args.inpdir, datestring, 
                        sensor, platform, idnumber, args.ecfsdir)
    else:
        print (" ! Check your input directory, maybe it is empty ? \n")


    print ( " * %s finished !" % os.path.basename(__file__) )

