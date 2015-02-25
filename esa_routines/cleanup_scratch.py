#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
# C. Schlundt, December 2014, original version
# C. Schlundt, January 2015, delete config files added
#

import argparse
import os
import sys

from pycmsaf.logger import setup_root_logger

from housekeeping import delete_dir, get_id
from housekeeping import get_config_file_dict
from housekeeping import delete_file

logger = setup_root_logger(name='sissi')


def clear_l1(args_l1):
    """
    Remove L1 satellite input data if retrieval was successful.
    """

    # find platform
    if args_l1.satellite.upper() == "TERRA" or \
                    args_l1.satellite.upper() == "MOD":
        platform = "MOD"
        sensor = "MODIS"

    elif args_l1.satellite.upper() == "AQUA" or \
                    args_l1.satellite.upper() == "MYD":
        platform = "MYD"
        sensor = "MODIS"

    elif args_l1.satellite.upper().startswith("NOAA"):
        platform = args_l1.satellite.lower()
        sensor = "AVHRR"

    elif args_l1.satellite.upper().startswith("METOP"):
        platform = args_l1.satellite.lower()
        sensor = "AVHRR"

    else:
        logger.info("WRONG SATELLITE NAME!")
        sys.exit(0)

    # find corr. config file and delete it
    cfgdict = get_config_file_dict()
    strlist = list()

    for key in cfgdict:
        if "1" in key and sensor.lower() in key:
            strlist.append(key)
            for key2 in cfgdict[key]:
                strlist.append(cfgdict[key][key2])

    if len(strlist) != 4:
        logger.info("No information for cfg filename found in dictionary!")
        logger.info("Thus, config file cannot be deleted!")

    fname = strlist[1] + strlist[0] + '_' + \
            str(args_l1.year) + '_' + str('%02d' % args_l1.month) + \
            '_' + args_l1.satellite.upper() + strlist[2]

    splitpath = os.path.split(args_l1.inpdir)
    cfgfile = os.path.join(splitpath[0], strlist[3], fname)

    if os.path.isfile(cfgfile):
        logger.info("Delete: \'{0}\'".format(cfgfile))
        delete_file(cfgfile)
    else:
        logger.info("Nothing to delete: \'{0}\' doesn't exist!".
                format(cfgfile))

    ipath = os.path.join(args_l1.inpdir, sensor, platform,
                         str(args_l1.year), str('%02d' % args_l1.month))

    if os.path.isdir(ipath):
        logger.info("Delete: \'{0}\' -> retrieval was successful!".
                format(ipath))
        delete_dir(ipath)

    else:
        logger.info("Nothing to delete: \'{0}\' doesn't exist!".
                format(ipath))


def clear_l2(args_l2):
    """
    Search for ID and then remove all directories,
    which belong to this ID and satellite and sensor and date.
    """
    if args_l2.satellite.upper() == "TERRA":
        platform = "TERRA"
    elif args_l2.satellite.upper() == "AQUA":
        platform = "AQUA"
    elif args_l2.satellite.upper() == "MOD":
        platform = "TERRA"
    elif args_l2.satellite.upper() == "MYD":
        platform = "AQUA"
    elif args_l2.satellite.upper().startswith("NOAA"):
        platform = args_l2.satellite.lower()
    elif args_l2.satellite.upper().startswith("METOP"):
        platform = args_l2.satellite.lower()
    else:
        logger.info("WRONG SATELLITE NAME!")
        sys.exit(0)

    # find corr. config file and delete it
    cfgdict = get_config_file_dict()
    strlist = list()

    for key in cfgdict:
        if "2" in key:
            strlist.append(key)
            for key2 in cfgdict[key]:
                strlist.append(cfgdict[key][key2])

    if len(strlist) != 4:
        logger.info("No information for cfg filename found in dictionary!")
        logger.info("Thus, config file cannot be deleted!")

    fname = strlist[1] + strlist[0] + '_' + \
            str(args_l2.year) + '_' + str('%02d' % args_l2.month) + \
            '_' + args_l2.satellite.upper() + strlist[2]

    splitpath = os.path.split(args_l2.inpdir)
    cfgfile = os.path.join(splitpath[0], strlist[3], fname)

    if os.path.isfile(cfgfile):
        logger.info("Delete: \'{0}\' ".format(cfgfile))
        delete_file(cfgfile)
    else:
        logger.info("Nothing to delete: \'{0}\' doesn't exist!".
                format(cfgfile))

    # date string
    datestr = str(args_l2.year) + str('%02d' % args_l2.month)

    # get dirs list containing all subdirs of given path
    alldirs = os.listdir(args_l2.inpdir)

    # if alldirs is not empty
    if len(alldirs) > 0:

        # get dirs list matching the arguments
        getdirs = list()
        for ad in alldirs:
            if datestr in ad \
                    and args_l2.instrument.upper() in ad \
                    and platform in ad and 'retrieval' in ad:
                getdirs.append(ad)

        # check if getdirs list is empty
        if len(getdirs) == 0:
            logger.info("Nothing to delete in {0} for {1} {2} {3}".
                    format(args_l2.inpdir, args_l2.instrument.upper(), platform, datestr))
        else:
            # sort list
            getdirs.sort()

            # get last element from list, should be last job
            lastdir = getdirs.pop()

            # get ID number from the last job
            id_number = get_id(lastdir)

            # remove all subdirs matching the id number
            for gdir in getdirs:
                if id_number in gdir:
                    logger.info("Delete: {0}".format(gdir))
                    delete_dir(gdir)

            # pattern
            pattern = datestr + '*' + args_l2.instrument.upper() + '_' + \
                      platform + '_retrieval_' + id_number

            # remove all dirs matching pattern
            logger.info("Delete: \'{0}\' -> retrieval failed or was successful!".
                format(pattern))
    else:
        logger.info("Nothing to delete in {0} for {1} {2} {3}".
            format(args_l2.inpdir, args_l2.instrument.upper(), platform, datestr))


def clear_l3(args_l3):
    """
    Remove L3 results if archiving was successful.
    """

    # find platform
    if args_l3.satellite.upper() == "TERRA" or \
                    args_l3.satellite.upper() == "MOD":
        platform = "TERRA"
        sensor = "MODIS"

    elif args_l3.satellite.upper() == "AQUA" or \
                    args_l3.satellite.upper() == "MYD":
        platform = "AQUA"
        sensor = "MODIS"

    elif args_l3.satellite.upper().startswith("NOAA"):
        platform = args_l3.satellite.upper()
        sensor = "AVHRR"

    elif args_l3.satellite.upper().startswith("METOP"):
        platform = args_l3.satellite.upper()
        sensor = "AVHRR"

    else:
        logger.info("WRONG SATELLITE NAME!")
        sys.exit(0)

    # find corr. config files and delete them (l3u, l3c)
    numcfgs = 2
    cfgdict = get_config_file_dict()
    strlist = list()

    for key in cfgdict:
        if "3" in key:
            strlist.append(key)
            for key2 in cfgdict[key]:
                strlist.append(cfgdict[key][key2])

    if len(strlist) != 4 * numcfgs:
        logger.info("No information for cfg filename found in dictionary!")
        logger.info("Thus, config file cannot be deleted!")

    nc = 0
    while nc < numcfgs:

        cnt = nc * (len(strlist) / numcfgs)

        fname = strlist[1 + cnt] + strlist[0 + cnt] + '_' + \
                str(args_l3.year) + '_' + str('%02d' % args_l3.month) + \
                '_' + args_l3.satellite.upper() + strlist[2 + cnt]

        splitpath = os.path.split(os.path.split(args_l3.inpdir)[0])
        cfgfile = os.path.join(splitpath[0], strlist[3 + cnt], fname)

        if os.path.isfile(cfgfile):
            logger.info("Delete: \'{0}\' ".format(cfgfile))
            delete_file(cfgfile)
        else:
            logger.info("Nothing to delete: \'{0}\' doesn't exist!".
                    format(cfgfile))

        nc += 1

    # date string
    datestr = str(args_l3.year) + str('%02d' % args_l3.month)

    # get dirs list containing all subdirs of given path
    alldirs = os.listdir(args_l3.inpdir)

    if len(alldirs) > 0:
        # get dirs list matching the arguments
        getdirs = list()
        for ad in alldirs:
            if datestr in ad and sensor in ad \
                    and 'ORAC' in ad and platform in ad:
                getdirs.append(ad)

        # check if getdirs list is empty
        if len(getdirs) == 0:
            logger.info("Nothing to delete in {0} for {1} {2} {3}".
                    format(args_l3.inpdir, sensor, platform, datestr))
        else:
            # sort list
            getdirs.sort()

            # get last element from list, should be last job
            lastdir = getdirs.pop()

            # get ID number from the last job
            id_num = get_id(lastdir)

            # remove all subdirs matching the id number
            for gdir in getdirs:
                if id_num in gdir:
                    logger.info("Delete: {0}".format(gdir))
                    delete_dir(gdir)

            # pattern
            pattern = datestr + '*' + sensor + '_ORAC*' + \
                      platform + '*' + id_num

            # remove all dirs matching pattern
            logger.info("Delete: \'{0}\' -> L2toL3 was successful!".
                    format(pattern))
    else:
        logger.info("Nothing to delete in {0} for {1} {2} {3}".
                format(args_l3.inpdir, sensor, platform, datestr))


def clear_aux(args_aux):
    """
    Remove auxiliary data if complete month was successful.
    """

    ipath = os.path.join(args_aux.inpdir, args_aux.auxdata)

    if not os.path.isdir(ipath):
        logger.info("The argument for --auxdata should be equal "
            "to the name of the subfolder you want to clean up.")
        sys.exit(0)

    # find corr. config file and delete it
    cfgdict = get_config_file_dict()
    strlist = list()

    if args_aux.auxdata.lower().startswith("aux"):
        auxkey = "aux"
    elif args_aux.auxdata.lower().startswith("era"):
        auxkey = "era"

    for key in cfgdict:
        # noinspection PyUnboundLocalVariable
        if "1" in key and auxkey in key:
            strlist.append(key)
            for key2 in cfgdict[key]:
                strlist.append(cfgdict[key][key2])

    if len(strlist) != 4:
        logger.info("No information for cfg filename found in dictionary!")
        logger.info("Thus, config file cannot be deleted!")

    fname = strlist[1] + strlist[0] + '_' + \
            str(args_aux.year) + '_' + \
            str('%02d' % args_aux.month) + strlist[2]

    splitpath = os.path.split(args_aux.inpdir)
    cfgfile = os.path.join(splitpath[0], strlist[3], fname)

    if os.path.isfile(cfgfile):
        logger.info("Delete: \'{0}\' ".format(cfgfile))
        delete_file(cfgfile)
    else:
        logger.info("Nothing to delete: \'{0}\' doesn't exist!".format(cfgfile))

    ilist = os.listdir(ipath)

    for i in ilist:

        if not i.isdigit():
            # aux
            ispath = os.path.join(ipath, i, str(args_aux.year),
                                  str('%02d' % args_aux.month))
        else:
            # ERAinterim
            ispath = os.path.join(ipath, str(args_aux.year),
                                  str('%02d' % args_aux.month))

        if os.path.isdir(ispath):
            logger.info("Delete: \'{0}\' -> month was successful!".
                    format(ispath))
            delete_dir(ispath)
        else:
            logger.info("Nothing to delete: \'{0}\' doesn't exist!".
                    format(ispath))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=u''' {0:s} removes directories/files/etc.
        for given data and date.'''.format(os.path.basename(__file__)))

    # add main arguments
    parser.add_argument('--inpdir', type=str, required=True,
                        help="String: /path/where/to/search")

    parser.add_argument('--year', type=int, required=True,
                        help="Integer: yyyy, e.g. 2008")

    parser.add_argument('--month', type=int, required=True,
                        help="Integer: mm, e.g. 1")

    # define subcommands
    subparsers = parser.add_subparsers(help="Select a Subcommand")

    # -> remove l1 satellite data if retrieval was successful
    clear_l1_parser = subparsers.add_parser('clear_l1',
                                            description="Remove L1 input data if "
                                                        "retrieval was successful")
    clear_l1_parser.add_argument('--satellite', type=str, required=True,
                                 help="String, e.g. noaa18, TERRA, MYD")
    clear_l1_parser.add_argument('--instrument', type=str, required=True,
                                 help="String, e.g. AVHRR, MODIS")
    clear_l1_parser.set_defaults(func=clear_l1)

    # -> remove retrieval subfolders
    clear_l2_parser = subparsers.add_parser('clear_l2',
                                            description="Clean up if retrieval.ecf "
                                                        "failed or was successful.")
    clear_l2_parser.add_argument('--satellite', type=str, required=True,
                                 help="String, e.g. noaa18, TERRA, MYD")
    clear_l2_parser.add_argument('--instrument', type=str, required=True,
                                 help="String, e.g. AVHRR, MODIS")
    clear_l2_parser.set_defaults(func=clear_l2)

    # -> remove l2tol3 subfolders
    clear_l3_parser = subparsers.add_parser('clear_l3',
                                            description="Clean up if l2tol3 "
                                                        "failed or was successful.")
    clear_l3_parser.add_argument('--satellite', type=str, required=True,
                                 help="String, e.g. noaa18, TERRA, MYD")
    clear_l3_parser.add_argument('--instrument', type=str, required=True,
                                 help="String, e.g. AVHRR, MODIS")
    clear_l3_parser.set_defaults(func=clear_l3)

    # -> remove auxiliary dataset if month was successful
    clear_aux_parser = subparsers.add_parser('clear_aux',
                                             description="Remove auxiliary data if "
                                                         "month was successfully processed")
    clear_aux_parser.add_argument('--auxdata', type=str, required=True,
                                  help="String: e.g. \'aux\', \'ERAinterim\'")
    clear_aux_parser.set_defaults(func=clear_aux)

    # Parse arguments
    args = parser.parse_args()

    # Call function associated with the selected subcommand
    logger.info("*** {0} start for {1}".format(sys.argv[0], args))
    args.func(args)

    logger.info("*** {0} succesfully finished \n".format(sys.argv[0]))
