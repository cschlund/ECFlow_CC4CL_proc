#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#
# C.Schlundt: November, 2014, l3 data
# C.Schlundt: January, 2015, l2 data
#

import os
import sys
import argparse

from housekeeping import get_id, delete_dir
from housekeeping import split_platform_string
from housekeeping import tar_results
from housekeeping import copy_into_ecfs

from pycmsaf.logger import setup_root_logger
logger = setup_root_logger(name='sissi')


def l2(args_l2):
    """
    Subcommand for archiving L2 data into ECFS.
    """
    # -- create date string
    datestring = str(args_l2.year) + str('%02d' % args_l2.month)

    # -- sensor and platform settings
    if args_l2.instrument.upper() == "AVHRR":
        (satstr, satnum) = split_platform_string(args_l2.satellite)
        sensor = args_l2.instrument.upper()
        platform = satstr.upper() + '-' + satnum
    else:
        sensor = args_l2.instrument.upper()
        platform = args_l2.satellite.upper()

    # -- list everything in input directory
    alldirs = os.listdir(args_l2.inpdir)

    # -- list of files to be archived
    tarfile_list = list()

    # *** L2 archiving ***

    # -- find latest job via ID-US number
    if len(alldirs) > 0:
        getdirs = list()
        # collect right subfolders
        for ad in alldirs:
            if datestring in ad \
                    and args_l2.instrument.upper() in ad \
                    and args_l2.satellite.lower() in ad \
                    and 'retrieval' in ad:
                getdirs.append(ad)
        # sort list
        getdirs.sort()
        # get last element from list, should be last job
        lastdir = getdirs.pop()
        # get ID number from the last job
        idnumber = get_id(lastdir)

        # archive data
        (tlist, tempdir) = tar_results("L2", args_l2.inpdir,
                                       datestring, sensor,
                                       platform, idnumber)
        tarfile_list = tlist

    else:
        logger.info("Check your input directory, maybe it is empty ?")

    # copy tarfile into ECFS
    logger.info("Copy2ECFS: tarfile_list")
    copy_into_ecfs(datestring, tarfile_list, args_l2.ecfsdir)

    # delete tempdir
    logger.info("Delete \'{0}\'".format(tempdir))
    delete_dir(tempdir)


def l3(args_l3):
    """
    Subcommand for archiving l3 data into ECFS.
    """
    # -- create date string
    datestring = str(args_l3.year) + str('%02d' % args_l3.month)

    # -- sensor and platform settings
    if args_l3.instrument.upper() == "AVHRR":
        (satstr, satnum) = split_platform_string(args_l3.satellite)
        sensor = args_l3.instrument.upper()
        platform = satstr.upper() + '-' + satnum
    else:
        sensor = args_l3.instrument.upper()
        platform = args_l3.satellite.upper()

    # -- list everything in input directory
    alldirs = os.listdir(args_l3.inpdir)

    # *** L3C archiving ***
    if args_l3.prodtype.upper() == "L3C":

        # -- find latest job via ID-US number
        if len(alldirs) > 0:
            getdirs = list()
            # collect right subfolders
            for ad in alldirs:
                if datestring in ad \
                        and args_l3.instrument.upper() in ad \
                        and args_l3.satellite.upper() in ad \
                        and 'monthly_means' in ad: 
                            getdirs.append(ad)
            # sort list
            getdirs.sort()
            # get last element from list, should be last job
            lastdir = getdirs.pop()
            # get ID number from the last job
            idnumber = get_id(lastdir)
            # make tarfile
            (tlist_l3c, tempdir_l3c) = tar_results(args_l3.prodtype.upper(), args_l3.inpdir, 
                                                   datestring, sensor, platform, idnumber)
            logger.info("Copy2ECFS: {0}".format(tlist_l3c))
            copy_into_ecfs(datestring, tlist_l3c, args_l3.ecfsdir)
            logger.info("Delete \'{0}\'".format(tempdir_l3c))
            delete_dir(tempdir_l3c)

        else:
            logger.info("Check your input directory, maybe it is empty ?")

    # *** L3U archiving ***
    elif args_l3.prodtype.upper() == "L3U":

        # find latest job via ID-US number
        if len(alldirs) > 0:
            getdirs = list()
            # collect right subfolders
            for ad in alldirs:
                if datestring in ad \
                        and args_l3.instrument.upper() in ad \
                        and args_l3.satellite.upper() in ad \
                        and 'daily_samples' in ad: 
                            getdirs.append(ad)
            # sort list
            getdirs.sort()
            # get last element from list, should be last job
            lastdir = getdirs.pop()
            # get ID number from the last job
            idnumber = get_id(lastdir)
            # make tarfile
            (tlist_l3u, tempdir_l3u) = tar_results(args_l3.prodtype.upper(), args_l3.inpdir, 
                                                   datestring, sensor, platform, idnumber)
            logger.info("Copy2ECFS: {0}".format(tlist_l3u))
            copy_into_ecfs(datestring, tlist_l3u, args_l3.ecfsdir)
            logger.info("Delete \'{0:s}\'".format(tempdir_l3u))
            delete_dir(tempdir_l3u)

        else:
            logger.info("Check your input directory, maybe it is empty ?")

    # *** L3S archiving ***
    elif args_l3.prodtype.upper() == "L3S":
        logger.info("L3S archiving not yet coded!")

    else:
        logger.info("Nothing was archived for l3 parameters passed:")
        logger.info(" * INPDIR  :{0} ".format(args_l3.inpdir))
        logger.info(" * ECFSDIR :{0} ".format(args_l3.ecfsdir))
        logger.info(" * PRODTYPE:{0} ".format(args_l3.prodtype))


if __name__ == '__main__':
    # -- parser arguments
    parser = argparse.ArgumentParser(
        description="{0} creates tar files for, L2, L3U and L3C. "
                    "The subroutines are defined in "
                    "housekeeping.py.".format(os.path.basename(__file__)))

    # main arguments
    parser.add_argument('--instrument', type=str, required=True,
                        help='String, e.g. AVHRR')

    parser.add_argument('--satellite', type=str, required=True,
                        help='String, e.g. NOAA18')
    parser.add_argument('--year', type=int, required=True,
                        help='Integer, e.g. 2008')
    parser.add_argument('--month', type=int, required=True,
                        help='Integer, e.g. 1')

    # define subcommands
    subparsers = parser.add_subparsers(help="Select a Subcommand")

    # archive L2 data
    l2_parser = subparsers.add_parser('l2', description="Archive L2 data.")
    l2_parser.add_argument('--inpdir', type=str, required=True,
                           help='String, e.g. /path/to/output')
    l2_parser.add_argument('--ecfsdir', type=str, required=True,
                           help='String, e.g. /ecfs/path/to/L2/data')
    l2_parser.set_defaults(func=l2)

    # archive L3C and L3U data
    l3_parser = subparsers.add_parser('l3', description="Archive L3C, L3U, L3S data.")
    l3_parser.add_argument('--inpdir', type=str, required=True,
                           help='String, e.g. /path/to/output/level3')
    l3_parser.add_argument('--ecfsdir', type=str, required=True,
                           help='String, e.g. /ecfs/path/to/L3/data')
    l3_parser.add_argument('--prodtype', type=str, required=True,
                            help="Choices: \'L3U\', \'L3C\', \'L3S\'")
    l3_parser.set_defaults(func=l3)

    # Parse arguments
    args = parser.parse_args()

    # Call function associated with the selected subcommand
    logger.info("*** {0} start for {1}".format(sys.argv[0], args))
    args.func(args)

    logger.info("*** {0:s} succesfully finished \n".format(sys.argv[0]))
