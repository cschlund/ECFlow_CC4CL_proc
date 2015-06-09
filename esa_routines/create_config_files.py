#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
# C. Schlundt, November 2014
#

import os
import sys
import argparse
import time
import datetime

from pycmsaf.logger import setup_root_logger
from housekeeping import get_id

logger = setup_root_logger(name='sissi')


def getsat(args_sat):
    """
    Writes config file for dearchiving satellite data.
    @param args_sat: command line arguments
    """

    global platform
    try:
        if args_sat.satellite.upper() == "TERRA":
            platform = "MOD"
        elif args_sat.satellite.upper() == "AQUA":
            platform = "MYD"
        elif args_sat.satellite.upper().startswith("NOAA"):
            platform = args_sat.satellite.lower()
        elif args_sat.satellite.upper().startswith("METOP"):
            platform = args_sat.satellite.lower()
        else:
            logger.info("WRONG SATELLITE NAME!")
            sys.exit(0)

        ts = datetime.datetime.fromtimestamp(time.time())
        timestamp = ts.strftime("%Y-%m-%d %H:%M:%S")

        f = open(args_sat.cfile, mode="w")

        f.write("# Config file for dearchiving satellite data\n")
        f.write("# Created: {0}\n".format(timestamp))
        f.write("\n")
        f.write("# define date range\n")
        f.write("STARTYEAR={0}\n".format(str(args_sat.start_year)))
        f.write("STOPYEAR={0}\n".format(str(args_sat.end_year)))
        f.write("STARTMONTH={0}\n".format(str(args_sat.start_month)))
        f.write("STOPMONTH={0}\n".format(str(args_sat.end_month)))
        f.write("STARTDAY=1\n")
        f.write("STOPDAY=0\n")
        f.write("\n")
        f.write("#define sensor and platform\n")
        f.write("instrument={0}\n".format(args_sat.instrument.upper()))
        f.write("platform={0}\n".format(platform))
        if args_sat.instrument.upper() == "MODIS":
            f.write("\n")
            f.write("cflag=0\n")
            f.write("rflag=1\n")
            f.write("rcut=50\n")
        f.close()

    except (IndexError, ValueError, RuntimeError, Exception) as err:
        logger.info("FAILED: {0}".format(err))

    return


def getaux(args_aux):
    """
    Writes config file for dearchiving auxiliary data.
    @param args_aux: command line arguments
    """

    try:
        ts = datetime.datetime.fromtimestamp(time.time())
        timestamp = ts.strftime("%Y-%m-%d %H:%M:%S")

        f = open(args_aux.cfile, mode="w")

        f.write("# Config file for dearchiving auxiliary data\n")
        f.write("# Created: {0}\n".format(timestamp))
        f.write("\n")
        f.write("# define date range\n")
        f.write("STARTYEAR={0}\n".format(str(args_aux.start_year)))
        f.write("STOPYEAR={0}\n".format(str(args_aux.end_year)))
        f.write("STARTMONTH={0}\n".format(str(args_aux.start_month)))
        f.write("STOPMONTH={0}\n".format(str(args_aux.end_month)))
        f.write("STARTDAY=1\n")
        f.write("STOPDAY=0\n")
        if args_aux.getdata == "aux":
            f.write("\n")
            f.write("albedo_type=MCD43C3\n")
            f.write("albedo_suffix=.tar\n")
            f.write("BRDF_type=MCD43C1\n")
            f.write("BRDF_suffix=.tar\n")
            f.write("ice_snow_type=NISE_SSMI*\n")
            f.write("ice_snow_suffix=.tar\n")
            f.write("emissivity_type=global_emis_inf10_monthFilled_MYD11C3.A\n")
            if 2003 <= args.start_year <= 2006 and 2003 <= args.end_year <= 2006:
                # between 2003 and 2006 filename extension
                f.write("emissivity_suffix=.nc.bz2\n")
            else:
                # from 2007 onwards and for climatology filename
                f.write("emissivity_suffix=.041.nc.bz2\n")
        f.close()

    except (IndexError, ValueError, RuntimeError, Exception) as err:
        logger.info("FAILED: {0}".format(err))

    return


def proc2(args_ret):
    """
    Writes config file for the retrieval.
    @param args_ret: command line arguments
    """

    global platform
    try:
        if args_ret.satellite.upper() == "TERRA":
            # platform="MOD"
            platform = "TERRA"
        elif args_ret.satellite.upper() == "AQUA":
            # platform="MYD"
            platform = "AQUA"
        elif args_ret.satellite.upper().startswith("NOAA"):
            platform = args_ret.satellite.lower()
        elif args_ret.satellite.upper().startswith("METOP"):
            platform = args_ret.satellite.lower()
        else:
            logger.info("WRONG SATELLITE NAME!")
            sys.exit(0)

        ts = datetime.datetime.fromtimestamp(time.time())
        timestamp = ts.strftime("%Y-%m-%d %H:%M:%S")

        f = open(args_ret.cfile, mode="w")

        f.write("# Config file for proc2 (ORAC) \n")
        f.write("# Created: {0}\n".format(timestamp))
        f.write("\n")
        f.write("nthreads=1\n")
        f.write("wrapper_mode=dyn\n")
        f.write("\n")
        f.write("# define date range\n")
        f.write("STARTYEAR={0}\n".format(str(args_ret.start_year)))
        f.write("STOPYEAR={0}\n".format(str(args_ret.end_year)))
        f.write("STARTMONTH={0}\n".format(str(args_ret.start_month)))
        f.write("STOPMONTH={0}\n".format(str(args_ret.end_month)))

        if args_ret.procday < 0:
            f.write("STARTDAY=1\n")
            f.write("STOPDAY=0\n")
        else:
            f.write("STARTDAY={0}\n".format(str(args_ret.procday)))
            f.write("STOPDAY={0}\n".format(str(args_ret.procday)))

        f.write("\n")
        f.write("# define sensor and platform\n")
        f.write("instrument={0}\n".format(args_ret.instrument.upper()))
        f.write("platform={0}\n".format(platform))
        f.write("\n")
        f.write("# this defines the preprocessing grid\n")
        f.write("# 1: ecmwf grid, 2: L3 grid, 3: own definition\n")
        f.write("gridflag=3\n")
        f.write("# this is the inverse of the actual increment\n")
        f.write("dellon=2.0\n")
        f.write("dellat=2.0\n")
        f.write("\n")
        f.write("# start and end pixel in across/along track direction\n")
        if args_ret.testrun is True:
            f.write("# subset for testing\n")
            f.write("startx=200\n")
            f.write("endx=210\n")
            f.write("starty=200\n")
            f.write("endy=210\n")
        else:
            f.write("# full orbits\n")
            f.write("startx=-1\n")
            f.write("endx=-1\n")
            f.write("starty=-1\n")
            f.write("endy=-1\n")
        f.write("\n")
        f.write("# This controls the use of channels (to be modified)\n")
        f.write("# \'0\': use all channels (for MODIS where they are all available)\n")
        f.write("# \'1\': use 1.6mum channel and NOT 3.4\n")
        f.write("# \'3\': use 3.4 mum channel and NOT 1.6\n")
        f.write("# \'2\': pick \'1\' OR \'3\'automatically \n")
        f.write("#      depending on which AVHRR is just processed.\n")
        f.write("#      (to be implemented)\n")
        f.write("channelflag=0\n")
        f.write("# number of channels available in files coming from preprocessing\n")
        f.write("nchannels_avail=6\n")
        f.write("# number of channels to use from those\n")
        f.write("nchannels=${nchannels_avail}\n")
        f.write("# channel indices to use\n")
        f.write("proc_flag[0]=1   # ch1\n")
        f.write("proc_flag[1]=1   # ch2\n")
        f.write("proc_flag[2]=1   # ch3a\n")
        f.write("proc_flag[3]=1   # ch3b\n")
        f.write("proc_flag[4]=1   # ch4\n")
        f.write("proc_flag[5]=1   # ch5\n")
        f.write("\n")
        f.write("# control the behavior of the postprocessing\n")
        f.write("minre_i=0.1\n")
        f.write("minre_w=0.1\n")
        f.write("maxre_i=200.0\n")
        f.write("maxre_w=30.0\n")
        f.write("minod_i=0.1\n")
        f.write("minod_w=0.1\n")
        f.write("maxod_i=999.0\n")
        f.write("maxod_w=999.0\n")
        f.write("maxcost=1000000.0\n")
        f.write("costfactor=1.5\n")
        f.write("lsec=1\n")
        f.write("lstrict=0\n")
        f.write("# cloud mask thresholds\n")
        f.write("cotthres=1.39\n")
        f.write("cotthres1=0.2\n")
        f.write("cotthres2=0.3\n")
        f.write("# temperature threshold for stemp-ctt difference\n")
        f.write("# (keep equal for all three variables (heights))\n")
        f.write("tempthres_h=19.0\n")
        f.write("tempthres_m=19.0\n")
        f.write("tempthres_l=19.0\n")
        f.write("tempthres1=14.0\n")
        f.write("ctt_thres=280.0\n")
        f.write("ctt_bound=150.0\n")
        f.write("ctt_bound_winter=275.0\n")
        f.write("ctt_bound_summer=295.0\n")
        f.write("ctp_thres=907.0\n")
        f.write("ctp_thres1=957.0\n")
        f.write("ctp_bound=50.0\n")
        f.write("ctp_bound_up=1100.0\n")
        f.write("# obsolete\n")
        f.write("ctp_udivctp=100000.0\n")
        f.write("# some static info\n")
        f.write("# this is all related to AATSR, set these as dummies\n")
        f.write("# as DWD does not do AATSR processing:\n")
        f.write("aatsr_calib_file='n/a'\n")
        f.write("# flag=3, i.e. use single ERA interim netcdf file\n")
        f.write("badc=3\n")
        f.write("ecmwf_path2='n/a'\n")
        f.write("ecmwf_path3='n/a'\n")
        f.write("cchunkproc=0\n")
        f.write("day_nightc=0\n")
        f.write("cverbose='T'\n")
        f.write("cchunk='F'\n")
        f.write("cfullpath='T'\n")
        f.write("cinclude_full_brdf='T'\n")
        f.write("RTTOV_version='11'\n")
        f.write("ECMWF_version='ERA-Interim'\n")
        f.write("SVN_version='"+args_ret.svn_version+"'\n")
        f.close()

    except (IndexError, ValueError, RuntimeError, Exception) as err:
        logger.info("FAILED: {0}".format(err))

    return


# -------------------------------------------------------------------
def l2tol3(args_l3):
    """
    Writes config file for the l2 to l3 processing:
    l3a = L3C
    l3b = L3S
    @param args_l3: command line arguments
    """
    try:
        ts = datetime.datetime.fromtimestamp(time.time())
        timestamp = ts.strftime("%Y-%m-%d %H:%M:%S")

        f = open(args_l3.cfile, mode="w")

        f.write("# Config file for level3 processing\n")
        f.write("# Created: {0}\n".format(timestamp))
        f.write("\n")
        f.write("# define date range\n")
        f.write("YEAR={0}\n".format(str(args_l3.start_year)))
        f.write("MONTH={0}\n".format(str(args_l3.start_month)))
        f.write("DAY=-1\n")
        f.write("\n")
        f.write("# define sensor and platform\n")
        f.write("sensor={0}\n".format(args_l3.instrument.upper()))

        # for L3C/l3a yes, but not for L3S/l3b (super-collated)
        if args_l3.prodtype.lower() == "l3a" and args_l3.satellite:
            f.write("platform={0}\n".format(args_l3.satellite.upper()))

        f.write("\n")
        f.write("# define product type\n")
        f.write("prodtype={0}\n".format(args_l3.prodtype))
        f.write("\n")
        f.write("# set here some details about the grid:\n")
        f.write("# produce global grid (F) or local grid (T)\n")
        f.write("local=F\n")
        f.write("\n")
        f.write("# for global grid (local=F) the following parameters\n")
        f.write("# are set internally in the source-code\n")
        f.write("# details of local grid:\n")
        f.write("# europe with surrounding areas\n")
        f.write("slon=0\n")
        f.write("elon=18\n")
        f.write("slat=42\n")
        f.write("elat=53\n")
        f.write("# switzerland\n")
        f.write("#slon=5\n")
        f.write("#elon=11\n")
        f.write("#slat=45\n")
        f.write("#elat=48\n")
        f.write("\n")
        f.write("# inverse spacing of l3 and l2b grid in deg. for local grid\n")
        f.write("gridxl3=2\n")
        f.write("gridyl3=2\n")
        f.write("\n")
        f.write("gridxl2b=10\n")
        f.write("gridyl2b=10\n")
        f.write("\n")
        f.write("# inverse spacing of local grid in deg.\n")
        f.write("gridxloc=10\n")
        f.write("gridyloc=10\n")
        f.write("# filelist containing input files for product generation\n")
        f.write("filelist_l2b_sum_output={0}\n".format(args_l3.l2bsum_filelist))
        f.write("\n")

        f.close()

    except (IndexError, ValueError, RuntimeError, Exception) as err:
        logger.info("FAILED: {0}".format(err))

    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=u" {0:s} creates config files for given "
                    u"satellite, sensor, start and end dates "
                    u"required by CC4CL.".format(os.path.basename(__file__)))

    # add main arguments
    parser.add_argument('-cf', '--cfile', type=str, required=True,
                        help="String, e.g. /path/to/config_name.file")

    parser.add_argument('-sy', '--start_year', type=int,
                        help="Integer, e.g. 2010", required=True)

    parser.add_argument('-ey', '--end_year', type=int,
                        help="Integer, e.g. 2010", required=True)

    parser.add_argument('-sm', '--start_month', type=int,
                        help="Integer, e.g. 1", required=True)

    parser.add_argument('-em', '--end_month', type=int,
                        help="Integer, e.g. 1", required=True)

    # define subcommands
    subparsers = parser.add_subparsers(help="Select a Subcommand")

    # -> create config file for dearchiving avhrr/modis data
    getsat_parser = subparsers.add_parser('getsat',
                                          description="Make config file for dearchiving "
                                                      "avhrr or modis data.")
    getsat_parser.add_argument('-sat', '--satellite', required=True, type=str,
                               help="String, e.g. noaa18, terra")
    getsat_parser.add_argument('-ins', '--instrument', required=True, type=str,
                               help="String, e.g. avhrr, modis")
    getsat_parser.set_defaults(func=getsat)

    # -> create config file for dearchiving aux/mars data
    getaux_parser = subparsers.add_parser('getaux',
                                          description="Make config file for dearchiving "
                                                      "auxiliary or era interim data.")
    getaux_parser.add_argument('-get', '--getdata', required=True, type=str,
                               help="Choice: \'aux\' or \'era\'.")
    getaux_parser.set_defaults(func=getaux)

    # -> create config file for proc2 (ORAC)
    proc2_parser = subparsers.add_parser('proc2',
                                         description="Make config file for proc2,"
                                                     "i.e. generate L2 output.")
    proc2_parser.add_argument('-sat', '--satellite', required=True, type=str,
                              help="String, e.g. noaa18, terra")
    proc2_parser.add_argument('-ins', '--instrument', required=True, type=str,
                              help="String, e.g. avhrr, modis")
    proc2_parser.add_argument('-test', '--testrun', action="store_true",
                              help="Testrun: only a few pixels are processed, "
                                   "i.e. across: 200-210, along: 200-210")
    proc2_parser.add_argument('-pday', '--procday', type=int,
                              help="-1: whole month otherwise this day")
    proc2_parser.add_argument('-svn', '--svn_version', type=str, required=True,
                              help="SVN version of orac repository")
    proc2_parser.set_defaults(func=proc2)

    # -> create config file for l2 to l3 processing
    l2tol3_parser = subparsers.add_parser('l2tol3',
                                          description="Make config file for l2tol3, "
                                                      "i.e. generate L3U or L3S output.")
    # L3S: no satellite, sensor family monthly averages
    l2tol3_parser.add_argument('-sat', '--satellite', type=str,
                               help="String, e.g. noaa18, terra")
    #l2tol3_parser.add_argument('-sat', '--satellite', required=True, type=str,
    #                           help="String, e.g. noaa18, terra")
    l2tol3_parser.add_argument('-ins', '--instrument', required=True, type=str,
                               help="String, e.g. avhrr, modis")
    l2tol3_parser.add_argument('-inp', '--inpdir', required=True, type=str,
                               help="String, /path/to/input/files")
    l2tol3_parser.add_argument('-typ', '--prodtype', type=str,
                               help="Choices: \'l3a\' = L3U or \'l3b\' = L3S")
    l2tol3_parser.add_argument('-lfl', '--l2bsum_filelist', type=str,
                               help="String, /path/to/filelist/of/l2bsum/files")
    l2tol3_parser.set_defaults(func=l2tol3)

    # Parse arguments
    args = parser.parse_args()

    # Call function associated with the selected subcommand
    logger.info("*** {0} start for {1}".format(sys.argv[0], args))
    args.func(args)

    logger.info("*** {0} succesfully finished \n".format(sys.argv[0]))
