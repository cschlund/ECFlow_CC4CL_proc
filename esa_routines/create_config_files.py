#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
# C. Schlundt, November 2014
#

import os, sys
import argparse
import time, datetime

# -------------------------------------------------------------------
def get_id( tmpdir ):
    '''
    Split string and find ID...US... number.
    '''
    split = tmpdir.split('_')

    for i in split:
        if i.startswith('ID'):
            id = i
        elif i.startswith('US'):
            us = i
        else:
            pass

    return id+'_'+us

# -------------------------------------------------------------------
def getsat(args):
    try: 

        if args.satellite.upper() == "TERRA":
            platform="MOD"
        elif args.satellite.upper() == "AQUA":
            platform="MYD"
        elif args.satellite.upper().startswith("NOAA"):
            platform=args.satellite.lower()
        elif args.satellite.upper().startswith("METOP"):
            platform=args.satellite.lower()
        else:
            print " ! Wrong satellite name !\n"
            exit(0)

        ts = datetime.datetime.fromtimestamp(time.time())
        timestamp = ts.strftime("%Y-%m-%d %H:%M:%S")

        f = open(args.cfile, mode="w")
        f.write("# Config file for dearchiving satellite data\n")
        f.write("# Created: "+timestamp+"\n")
        f.write("\n")
        f.write("# define date range\n")
        f.write("STARTYEAR="+str(args.start_year)+"\n")
        f.write("STOPYEAR="+str(args.end_year)+"\n")
        f.write("STARTMONTH="+str(args.start_month)+"\n")
        f.write("STOPMONTH="+str(args.end_month)+"\n")
        f.write("STARTDAY=1\n")
        f.write("STOPDAY=0\n")
        f.write("\n")
        f.write("#define sensor and platform\n")
        f.write("instrument="+args.instrument.upper()+"\n")
        f.write("platform="+platform+"\n")
        if args.instrument.upper() == "MODIS": 
            f.write("\n")
            f.write("cflag=0\n")
            f.write("rflag=1\n")
            f.write("rcut=50\n")
        f.close()
    except (IndexError, ValueError, RuntimeError,
            Exception) as err:
        print (" --- FAILED: %s" % err)
        
    return

# -------------------------------------------------------------------
def getaux(args):
    try: 

        ts = datetime.datetime.fromtimestamp(time.time())
        timestamp = ts.strftime("%Y-%m-%d %H:%M:%S")

        f = open(args.cfile, mode="w")
        f.write("# Config file for dearchiving auxiliary data\n")
        f.write("# Created: "+timestamp+"\n")
        f.write("\n")
        f.write("# define date range\n")
        f.write("STARTYEAR="+str(args.start_year)+"\n")
        f.write("STOPYEAR="+str(args.end_year)+"\n")
        f.write("STARTMONTH="+str(args.start_month)+"\n")
        f.write("STOPMONTH="+str(args.end_month)+"\n")
        f.write("STARTDAY=1\n")
        f.write("STOPDAY=0\n")
        if args.getdata == "aux":
            f.write("\n")
            f.write("albedo_type=MCD43C3\n")
            f.write("albedo_suffix=.tar\n")
            f.write("BRDF_type=MCD43C1\n")
            f.write("BRDF_suffix=.tar\n")
            f.write("ice_snow_type=NISE_SSMI*\n") 
            f.write("ice_snow_suffix=.tar\n")
            f.write("emissivity_type=global_emis_inf10_monthFilled_MYD11C3.A\n")
            if args.start_year <= 2006 and args.end_year <= 2006:
                f.write("emissivity_suffix=.nc.bz2\n")
            else:
                f.write("emissivity_suffix=.041.nc.bz2\n")
        f.close()
    except (IndexError, ValueError, RuntimeError,
            Exception) as err:
        print (" --- FAILED: %s" % err)
        
    return

# -------------------------------------------------------------------
def proc2(args):
    try: 

        if args.satellite.upper() == "TERRA":
            #platform="MOD"
            platform="TERRA"
        elif args.satellite.upper() == "AQUA":
            #platform="MYD"
            platform="AQUA"
        elif args.satellite.upper().startswith("NOAA"):
            platform=args.satellite.lower()
        elif args.satellite.upper().startswith("METOP"):
            platform=args.satellite.lower()
        else:
            print " ! Wrong satellite name !\n"
            exit(0)

        ts = datetime.datetime.fromtimestamp(time.time())
        timestamp = ts.strftime("%Y-%m-%d %H:%M:%S")

        f = open(args.cfile, mode="w")
        f.write("# Config file for proc2 (ORAC) \n")
        f.write("# Created: "+timestamp+"\n")
        f.write("\n")
        f.write("nthreads=1\n")
        f.write("wrapper_mode=dyn\n")
        f.write("\n")
        f.write("# define date range\n")
        f.write("STARTYEAR="+str(args.start_year)+"\n")
        f.write("STOPYEAR="+str(args.end_year)+"\n")
        f.write("STARTMONTH="+str(args.start_month)+"\n")
        f.write("STOPMONTH="+str(args.end_month)+"\n")
        f.write("STARTDAY="+str(sday)+"\n")
        f.write("STOPDAY="+str(eday)+"\n")
        f.write("\n")
        f.write("# define sensor and platform\n")
        f.write("instrument="+args.instrument.upper()+"\n")
        f.write("platform="+platform+"\n")
        f.write("\n")
        f.write("# this defines the preprocessing grid\n")
        f.write("# 1: ecmwf grid, 2: L3 grid, 3: own definition\n")
        f.write("gridflag=3\n")
        f.write("# this is the inverse of the actual increment\n")
        f.write("dellon=2.0\n")
        f.write("dellat=2.0\n")
        f.write("\n")
        f.write("# start and end pixel in across/along track direction\n")
        if args.testrun is True: 
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
        f.write("#number of channels available in files coming from preprocessing\n")
        f.write("nchannels_avail=6\n")
        f.write("#number of channels to use from those\n")
        f.write("nchannels=${nchannels_avail}\n")
        f.write("#channel indices to use\n")
        f.write("proc_flag[0]=1   # ch1\n")
        f.write("proc_flag[1]=1   # ch2\n")
        f.write("proc_flag[2]=0   # ch3a\n")
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
        f.write("aatsr_calib_file=''\n")
        f.write("# flag=3, i.e. use single ERA interim netcdf file\n")
        f.write("badc=3\n")
        f.write("ecmwf_path2=''\n")
        f.write("ecmwf_path3=''\n")
        f.write("cchunkproc=0\n")
        f.write("day_nightc=0\n")
        f.write("cverbose='T'\n")
        f.write("cchunk='F'\n")
        f.write("cfullpath='T'\n")
        f.write("cinclude_full_brdf='T'\n")
        f.close()
    except (IndexError, ValueError, RuntimeError,
            Exception) as err:
        print (" --- FAILED: %s" % err)
        
    return


# -------------------------------------------------------------------
def l2tol3(args):
    try: 

        if args.satellite.upper() == "TERRA":
            platform="MOD"
        elif args.satellite.upper() == "AQUA":
            platform="MYD"
        elif args.satellite.upper().startswith("NOAA"):
            platform=args.satellite.upper()
        elif args.satellite.upper().startswith("METOP"):
            platform=args.satellite.upper()
        else:
            print " ! Wrong satellite name !\n"
            exit(0)

        ts = datetime.datetime.fromtimestamp(time.time())
        timestamp = ts.strftime("%Y-%m-%d %H:%M:%S")

        # -- search for current ID number --

        # date string
        datestr = str(args.start_year)+str('%02d' % args.start_month)

        # get dirs list containing all subdirs of given path
        alldirs = os.listdir( args.inpdir )

        # get dirs list matching the arguments
        if len(alldirs) > 0:
            getdirs = list()
            for ad in alldirs:
                if datestr in ad \
                        and args.instrument.upper() in ad \
                        and args.satellite.lower() in ad \
                        and 'retrieval'in ad:
                            getdirs.append( ad )

            # sort list
            getdirs.sort()

            # get last element from list, should be last job
            lastdir = getdirs.pop()

            # get ID number from the last job
            id = get_id( lastdir )

        # -- end of search for current ID number --

        f = open(args.cfile, mode="w")
        f.write("# Config file for level3 processing\n")
        f.write("# Created: "+timestamp+"\n")
        f.write("\n")
        f.write("# define date range\n")
        f.write("YEAR="+str(args.start_year)+"\n")
        f.write("MONTH="+str(args.start_month)+"\n")
        f.write("DAY=-1\n")
        f.write("\n")
        f.write("# define sensor and platform\n")
        f.write("sensor="+args.instrument.upper()+"\n")
        f.write("platform="+platform+"\n")
        f.write("\n")
        f.write("# define product type\n")
        if args.prodtype == "l2b":
            f.write("prodtype=l2b\n")
        if args.prodtype == "l3a":
            f.write("prodtype=l3a\n")
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
        f.write("gridxl3=10\n")
        f.write("gridyl3=10\n")
        f.write("\n")
        f.write("gridxl2b=50\n")
        f.write("gridyl2b=50\n")
        f.write("\n")
        f.write("fastl3=0\n")
        f.write("\n")
        f.write("# obsolete:\n")
        f.write("l1closure=F\n")
        f.write("\n")
        f.write("# set id string explicitly in order to avoid\n")
        f.write("# confusion when averaging\n")
        #f.write("id=ID9314213_US1416834943\n")
        f.write("id="+id+"\n")
        f.write("\n")
        f.close()
    except (IndexError, ValueError, RuntimeError,
            Exception) as err:
        print (" --- FAILED: %s" % err)
        
    return


# -------------------------------------------------------------------
# --- main ---
# -------------------------------------------------------------------
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='''
            %s creates config files for given satellite,
            sensor, start and end dates required 
            by CC4CL.''' % os.path.basename(__file__))
    
    # add main arguments
    parser.add_argument('-cf', '--cfile', type=str,
            help="String, e.g. /path/to/config_name.file", 
            required=True)
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
            description='''Make config file for dearchiving 
            avhrr or modis data.''')
    getsat_parser.add_argument('-sat', '--satellite', 
            type=str, help="String, e.g. noaa18, terra", 
            required=True)
    getsat_parser.add_argument('-ins', '--instrument', 
            type=str, help="String, e.g. avhrr, modis", 
            required=True)
    getsat_parser.set_defaults(func=getsat)

    # -> create config file for dearchiving aux/mars data
    getaux_parser = subparsers.add_parser('getaux',
            description='''Make config file for dearchiving 
            auxiliary or era interim data.''')
    getaux_parser.add_argument('-get', '--getdata', 
            type=str, help="Choice: \'aux\' or \'era\'.", 
            required=True)
    getaux_parser.set_defaults(func=getaux)

    # -> create config file for proc2 (ORAC)
    proc2_parser = subparsers.add_parser('proc2',
            description='''Make config file for proc2,
            i.e. generate L2 output.''')
    proc2_parser.add_argument('-sat', '--satellite', 
            type=str, help="String, e.g. noaa18, terra", 
            required=True)
    proc2_parser.add_argument('-ins', '--instrument', 
            type=str, help="String, e.g. avhrr, modis", 
            required=True)
    proc2_parser.add_argument('-test', '--testrun',
            help='''Testrun: only a few pixels are processed, i.e.
            across: 200-210, along: 200-210''',
            action="store_true")
    proc2_parser.set_defaults(func=proc2)

    # -> create config file for l2 to l3 processing
    l2tol3_parser = subparsers.add_parser('l2tol3',
            description='''Make config file for l2tol3,
            i.e. generate L2B or L3A output.''')
    l2tol3_parser.add_argument('-sat', '--satellite', 
            type=str, help="String, e.g. noaa18, terra", 
            required=True)
    l2tol3_parser.add_argument('-ins', '--instrument', 
            type=str, help="String, e.g. avhrr, modis", 
            required=True)
    l2tol3_parser.add_argument('-inp', '--inpdir', 
            type=str, help="String, /path/to/input/files", 
            required=True)
    l2tol3_parser.add_argument('-typ', '--prodtype',
            help='''Choices: \'l2b\' == \'L3U\' or 
            \'l3a\' == \'L3C\' ''',
            type=str)
    l2tol3_parser.set_defaults(func=l2tol3)

    # Parse arguments
    args = parser.parse_args()

    # Testing: only one/few day(s)
    # Processing: eday=0 until last day of month
    sday = 1 #13
    eday = 0 #13

    # Call function associated with the selected subcommand
    args.func(args)


print ("\n *** %s finished for %s \n" % (sys.argv[0], args.cfile))


