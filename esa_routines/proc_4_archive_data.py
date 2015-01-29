#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#
# C.Schlundt: November, 2014, l3 data
# C.Schlundt: January, 2015, l2 data
#

import os, sys
import argparse
from housekeeping import get_id, delete_dir
from housekeeping import split_platform_string
from housekeeping import tar_results
from housekeeping import copy_into_ecfs

# -------------------------------------------------------------------
def l2(args):
    """
    Subcommand for archiving L2 data into ECFS.
    """
    
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

    # -- list of files to be archived
    tarfile_list = list()

    # *** L2 archiving ***

    # -- find latest job via ID-US number
    if len(alldirs) > 0:
        getdirs = list()
        # collect right subfolders
        for ad in alldirs:
            if datestring in ad \
                    and args.instrument.upper() in ad \
                    and args.satellite.lower() in ad \
                    and 'retrieval' in ad:
                        getdirs.append( ad )
        # sort list
        getdirs.sort()
        # get last element from list, should be last job
        lastdir = getdirs.pop()
        # get ID number from the last job
        idnumber = get_id( lastdir )

        #/archive data
        (tlist, tempdir) = tar_results( "L2", args.inpdir, 
                datestring, sensor, platform, idnumber)

        tarfile_list = tlist

    else:
        print (" ! Check your input directory, maybe it is empty ? \n")

    # copy tarfile into ECFS
    print (" * Copy2ECFS: tarfile_list")
    copy_into_ecfs( datestring, tarfile_list, args.ecfsdir )

    ## delete tempdir
    print (" * Delete \'%s\'" % tempdir)
    delete_dir( tempdir )


# -------------------------------------------------------------------
def l3(args):
    """
    Subcommand for archiving l3 data into ECFS.
    """

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

    # -- list of files to be archived
    tarfile_list = list()


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
        (tlist_l3c, tempdir_l3c) = tar_results( "L3C", args.inpdir, 
                datestring, sensor, platform, idnumber)

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
        (tlist_l3u, tempdir_l3u) = tar_results( "L3U", args.inpdir, 
                datestring, sensor, platform, idnumber)

    else:
        print (" ! Check your input directory, maybe it is empty ? \n")

    # list
    tarfile_list = tlist_l3c + tlist_l3u

    # copy tarfile into ECFS
    print (" * Copy2ECFS: tarfile_list")
    copy_into_ecfs( datestring, tarfile_list, args.ecfsdir )

    # delete tempdir
    print (" * Delete \'%s\'" % tempdir_l3u)
    delete_dir( tempdir_l3u )
    print (" * Delete \'%s\'" % tempdir_l3c)
    delete_dir( tempdir_l3c )


# -------------------------------------------------------------------
# --- main ---
# -------------------------------------------------------------------
if __name__ == '__main__': 

    # -- parser arguments
    parser = argparse.ArgumentParser(description='''%s
    creates tar files for, L2, L3U and L3C. 
    The subroutines are defined in "housekeeping.py".
    ''' % (os.path.basename(__file__)))
    
    # main arguments
    parser.add_argument('--instrument', type=str, required=True, 
            help='String, e.g. AVHRR')
    parser.add_argument('--satellite', type=str,required=True, 
            help='String, e.g. NOAA18')
    parser.add_argument('--year', type=int, required=True, 
            help='Integer, e.g. 2008')
    parser.add_argument('--month', type=int, required=True, 
            help='Integer, e.g. 1')

    # define subcommands
    subparsers = parser.add_subparsers(help="Select a Subcommand")

    # archive L2 data
    l2_parser = subparsers.add_parser('l2', 
            description="Archive L2 data.")
    l2_parser.add_argument('--inpdir', type=str, required=True, 
            help='String, e.g. /path/to/output')
    l2_parser.add_argument('--ecfsdir', type=str, required=True, 
            help='String, e.g. /ecfs/path/to/L2/data')
    l2_parser.set_defaults(func=l2)
    
    # archive L3C and L3U data
    l3_parser = subparsers.add_parser('l3', 
            description="Archive L3C and L3U data.")
    l3_parser.add_argument('--inpdir', type=str, required=True, 
            help='String, e.g. /path/to/output/level3')
    l3_parser.add_argument('--ecfsdir', type=str, required=True, 
            help='String, e.g. /ecfs/path/to/L3/data')
    l3_parser.set_defaults(func=l3)
    
    # Parse arguments
    args = parser.parse_args()
    
    print ("\n *** %s start for %s" % (sys.argv[0], args))

    # Call function associated with the selected subcommand
    args.func(args)

    print (" *** %s succesfully finished \n" % sys.argv[0])

# -------------------------------------------------------------------
