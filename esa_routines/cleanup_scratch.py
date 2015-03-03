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
import calendar

from pycmsaf.logger import setup_root_logger

from housekeeping import delete_dir, get_id
from housekeeping import get_config_file_dict
from housekeeping import delete_file

logger = setup_root_logger(name='sissi')

# must be equal to definitions in ./ecflow_suite/config_suite.py
cfg_prefix = "config_proc_"
cfg_suffix = ".file"


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


    # delete corr. config file
    # config_proc_1_getdata_avhrr_2008_01_NOAA15.file
    # config_proc_1_getdata_modis_2008_01_AQUA.file
    cfgfile = cfg_prefix + "1_getdata_" + sensor.lower() + '_' + \
              str(args_l1.year) + '_' + str('%02d' % args_l1.month) + \
              '_' + platform.upper() + cfg_suffix 

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


    # delete corr. config file
    # config_proc_2_process_2008_06_NOAA15.file
    # config_proc_2_process_2008_06_AQUA.file
    if "output" in args_l2.inpdir:

        cfgfile = cfg_prefix + "2_process_" + str(args_l2.year) + \
                  '_' + str('%02d' % args_l2.month) + \
                  '_' + platform.upper() + cfg_suffix 

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
                getdirs.append( os.path.join(args_l2.inpdir, ad) )

        # check if getdirs list is empty
        if len(getdirs) == 0:
            logger.info("Nothing to delete in {0} for {1} {2} {3}".
                    format(args_l2.inpdir, args_l2.instrument.upper(), platform, datestr))
        else:
            # sort list
            getdirs.sort()

            # get last element from list, should be last job
            lastdir = getdirs[-1]

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
    if args_l3.prodtype.lower() != "l3s":
        if args_l3.satellite:

            if args_l3.satellite.upper() == "TERRA" or \
                    args_l3.satellite.upper() == "MOD":
                platform = "TERRA"

            elif args_l3.satellite.upper() == "AQUA" or \
                    args_l3.satellite.upper() == "MYD":
                platform = "AQUA"

            elif args_l3.satellite.upper().startswith("NOAA"):
                platform = args_l3.satellite.upper()

            elif args_l3.satellite.upper().startswith("METOP"):
                platform = args_l3.satellite.upper()

            else:
                logger.info("WRONG SATELLITE NAME!")
                sys.exit(0)

        else:
            logger.info("You chose prodtype={0}, "
                        "so tell me which platform!".
                        format(args_l3.prodtype))
            sys.exit(0)

    # find sensor
    sensor = args_l3.instrument.upper()

    # delete corr. config file
    cfg_file_list = list()

    # -- monthly config files
    # config_proc_3_make_l3c_2008_01_NOAA18.file
    # config_proc_3_make_l3c_2008_01_AQUA.file
    if args_l3.prodtype.lower() == "l3c": 
        cfgfile = cfg_prefix + "3_make_" + args_l3.prodtype.lower() + \
                  '_' + str(args_l3.year) + '_' + str('%02d' % args_l3.month) + '_' + \
                  platform.upper() + cfg_suffix 
        cfg_file_list.append(cfgfile)

    # -- monthly config files
    # config_proc_3_make_l3s_2008_01_AVHRR.file
    # config_proc_3_make_l3s_2008_01_MODIS.file
    elif args_l3.prodtype.lower() == "l3s": 
        cfgfile = cfg_prefix + "3_make_" + args_l3.prodtype.lower() + \
                  '_' + str(args_l3.year) + '_' + str('%02d' % args_l3.month) + '_' + \
                  sensor.upper() + cfg_suffix 
        cfg_file_list.append(cfgfile)

    # -- daily config files
    # config_proc_3_make_l3u_NOAA18_2008_01_01.file
    # config_proc_3_make_l3u_TERRA_2008_01_31.file
    elif args_l3.prodtype.lower() == "l3u": 
        # calendar.monthrange
        # Returns weekday of first day of the month and 
        # number of days in month, for the specified year and month.
        last_day_of_month = calendar.monthrange(args_l3.year, args_l3.month)[1]
        for iday in range(last_day_of_month):
            iday += 1
            cfgfile = cfg_prefix + "3_make_" + args_l3.prodtype.lower() + '_' + \
                      platform.upper() + '_' + \
                      str(args_l3.year) + '_' + str('%02d' % args_l3.month) + '_' + \
                      str('%02d' % iday) + cfg_suffix 
            cfg_file_list.append(cfgfile)

    # -- daily config files
    # config_proc_3_make_l2b_sum_NOAA18_2008_01_01.file
    # config_proc_3_make_l2b_sum_NOAA18_2008_01_31.file
    elif args_l3.prodtype.lower() == "l2b_sum": 
        last_day_of_month = calendar.monthrange(args_l3.year, args_l3.month)[1]
        for iday in range(last_day_of_month):
            iday += 1
            cfgfile = cfg_prefix + "3_make_" + args_l3.prodtype.lower() + '_' + \
                      platform.upper() + '_' + \
                      str(args_l3.year) + '_' + str('%02d' % args_l3.month) + '_' + \
                      str('%02d' % iday) + cfg_suffix 
            cfg_file_list.append(cfgfile)

    # now remove all config files in the list
    for cfile in cfg_file_list:
        if os.path.isfile(cfile):
            logger.info("Delete: \'{0}\' ".format(cfile))
            delete_file(cfile)
        else:
            logger.info("Nothing to delete: \'{0}\' doesn't exist!".
                    format(cfile))


    # date string
    datestr = str(args_l3.year) + str('%02d' % args_l3.month)

    # get dirs list containing all subdirs of given path
    alldirs = os.listdir(args_l3.inpdir)

    if len(alldirs) > 0:
        # get dirs list matching the arguments
        getdirs = list()
        for ad in alldirs:
            # L3S: no platform, sensor fam. monthly averages
            if args_l3.prodtype.lower() == "l3s":
                if datestr in ad and sensor in ad \
                        and args_l3.prodtype.upper() in ad \
                        and 'ORAC' in ad:
                    getdirs.append( os.path.join(args_l3.inpdir, ad) )
            # L3C, L3U, L2B_SUM: sensor and platform in subdirectory_name
            else:
                if datestr in ad and sensor in ad \
                        and args_l3.prodtype.upper() in ad \
                        and 'ORAC' in ad and platform in ad:
                    getdirs.append( os.path.join(args_l3.inpdir, ad) )

        # check if getdirs list is empty
        if len(getdirs) == 0:
            logger.info("Nothing to delete in {0} for {1} {2} {3} {4}".
                    format(args_l3.inpdir, sensor, platform, datestr,
                           args_l3.prodtype.upper()))
        else:
            # sort list
            getdirs.sort()

            # get last element from list, should be last job
            lastdir = getdirs[-1]

            # get ID number from the last job
            id_num = get_id(lastdir)

            # remove all subdirs matching the id number
            for gdir in getdirs:
                if id_num in gdir:
                    logger.info("Delete: {0}".format(gdir))
                    delete_dir(gdir)

            # pattern
            # L3S: sensor fam. monthly averages
            if args_l3.prodtype.lower() == "l3s":
                pattern = datestr + '*' + sensor + '_ORAC*' + \
                          '*' + args_l3.prodtype.upper() + '*' + id_num
            else:
                pattern = datestr + '*' + sensor + '_ORAC*' + platform + \
                          '*' + args_l3.prodtype.upper() + '*' + id_num

            # remove all dirs matching pattern
            logger.info("Delete: \'{0}\' -> L2toL3 was successful!".
                    format(pattern))
    else:
        logger.info("Nothing to delete in {0} for {1} {2} {3} {4}".
                format(args_l3.inpdir, sensor, platform, datestr,
                       args_l3.prodtype))


def clear_aux(args_aux):
    """
    Remove auxiliary data if complete month was successful.
    """

    ipath = os.path.join(args_aux.inpdir, args_aux.auxdata)

    if not os.path.isdir(ipath):
        logger.info("The argument for --auxdata should be equal "
            "to the name of the subfolder you want to clean up.")
        sys.exit(0)


    # delete corr. config file
    # config_proc_1_getdata_aux_2008_01.file
    # config_proc_1_getdata_era_2008_01.file
    if args_aux.auxdata.lower().startswith("aux"):
        auxkey = "aux"
    elif args_aux.auxdata.lower().startswith("era"):
        auxkey = "era"

    cfgfile = cfg_prefix + "1_getdata_" + auxkey + '_' + \
              str(args_aux.year) + '_' + str('%02d' % args_aux.month) + \
              cfg_suffix 

    if os.path.isfile(cfgfile):
        logger.info("Delete: \'{0}\' ".format(cfgfile))
        delete_file(cfgfile)
    else:
        logger.info("Nothing to delete: \'{0}\' doesn't exist!".format(cfgfile))

    ilist = os.listdir(ipath)

    for i in ilist:

        if not i.isdigit():
            # aux
            # BRDF_dir # albedo_dir # emissivity_dir # ice_snow_dir
            ispath = os.path.join(ipath, i, str(args_aux.year),
                                  str('%02d' % args_aux.month))
        else:
            # ERAinterim
            # 2008
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
    # L3S: no satellite, sensor family monthly averages
    clear_l3_parser.add_argument('--satellite', type=str,
                                 help="String, e.g. noaa18, TERRA, MYD")
    #clear_l3_parser.add_argument('--satellite', type=str, required=True,
    #                             help="String, e.g. noaa18, TERRA, MYD")
    clear_l3_parser.add_argument('--instrument', type=str, required=True,
                                 help="String, e.g. AVHRR, MODIS")
    clear_l3_parser.add_argument('--prodtype', type=str, required=True,
                                 help="Choices: \'L2B_SUM\', \'L3U\', \'L3C\', \'L3S\'")
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
