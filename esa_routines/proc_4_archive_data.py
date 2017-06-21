#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#
# C.Schlundt: November, 2014, l3 data
# C.Schlundt: January, 2015, l2 data
#

import os
import sys
import argparse
import subprocess as sub
import fnmatch
from timeit import default_timer as timer

from housekeeping import get_id, delete_dir
from housekeeping import split_platform_string
from housekeeping import tar_results
from housekeeping import copy_into_ecfs
from housekeeping import move_files
from housekeeping import create_dir

from pycmsaf.logger import setup_root_logger
logger = setup_root_logger(name='sissi')

# temporary storage of L3 results
tmp_data_storage = "/scratch/ms/de/sf7/temp_cloudcci_level3_data"

def split_l3u(cdo_args, source, replace_string):
    target = source.replace("CLD_PRODUCTS", replace_string)
    target_interim = target + ".interim"
    call1 = 'cdo ' + cdo_args + " " + source + " " + target_interim
    call2 = 'nccopy -d5 ' + target_interim + " " + target
    call3 = 'rm -f ' + target_interim
    return " && ".join([call1, call2, call3])

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
    print "_______________________________________"
    print datestring

    # -- sensor and platform settings for L3U and L3C
    if args_l3.prodtype.upper() != "L3S" and args_l3.satellite:

        if args_l3.instrument.upper() == "AVHRR" and not args_l3.satellite.upper().startswith("METOP"):
            (satstr, satnum) = split_platform_string(args_l3.satellite)
            sensor = args_l3.instrument.upper()
            platform = satstr.upper() + '-' + satnum
        else:
            sensor = args_l3.instrument.upper()
            platform = args_l3.satellite.upper()

    elif args_l3.prodtype.upper() == "L3S":
        sensor = args_l3.instrument.upper()
        platform = "MERGED"
        print sensor + " " + platform
            
    else:
        logger.info("You chose prodtype={0},"
                    "thus give me also a satellite name".
                    format(args_l3.prodtype))
        sys.exit(0)

        
    # -- set prodtype_name
    if args_l3.prodtype.upper() == "L3U": 
        prodtype_name = "daily_samples"

    elif args_l3.prodtype.upper() == "L3C" or args_l3.prodtype.upper() == "L3S":
        prodtype_name = "monthly_means"

    else:
        logger.info("Wrong --prodtype input!")
        sys.exit(0)

        
    # -- list everything in input directory
    alldirs = os.listdir(args_l3.inpdir)

    # -- archive now: L3U or L3C (satellite AND instrument)
    if args_l3.prodtype.upper() != "L3S":

        # -- find latest job via ID-US number
        if len(alldirs) > 0:
            getdirs = list()

            # collect right subfolders
            for ad in alldirs:
                if args_l3.local:
                    if datestring in ad \
                            and args_l3.instrument.upper() in ad \
                            and args_l3.satellite.upper() in ad \
                            and args_l3.prodtype.upper() in ad \
                            and "Europe" in ad \
                            and prodtype_name in ad: 
                        getdirs.append(ad)
                else:
                    if datestring in ad \
                            and args_l3.instrument.upper() in ad \
                            and args_l3.satellite.upper() in ad \
                            and args_l3.prodtype.upper() in ad \
                            and "Europe" not in ad \
                            and prodtype_name in ad: 
                        getdirs.append(ad)                    

            # sort list
            getdirs.sort(key=lambda s: os.path.getmtime(os.path.join(args_l3.inpdir, s)), reverse=True)
            
            # get first element from list, should be last job
            lastdir = getdirs[0] 

            # get ID number from the last job
            idnumber = get_id(lastdir)
                       
            if args_l3.prodtype.upper() == "L3U":

                if args_l3.write_l3u_splitlist:

                    full_lastdir = os.path.join(args_l3.inpdir, lastdir)
                    for f in os.listdir(full_lastdir):
                        if ("CLD_PRODUCTS" in f and  f.endswith(".nc")):
                            full_f = os.path.join(full_lastdir, f)
                            p = sub.Popen(['cdo', 'sinfon', full_f],stdout=sub.PIPE,stderr=sub.PIPE)
                            output, errors = p.communicate()
                            # split at spaces, remove invalid entries and next-line strings
                            output = filter(None, output.split(" "))
                            output = [s.strip('\n') for s in output]

                    cld_products =  'selname,' + ','.join([s for s in output if "ctt_" in s or "cth_" in s or "ctp_" in s or "cer_" in s or ("cot_" in s and not "cccot_" in s) or "cwp_" in s or "stemp_" in s or "cph_" in s or "qcflag_" in s or "time_" in s])
                    cld_masktype =  'selname,' + ','.join([s for s in output if "cty_" in s or "cccot_" in s or "cmask_" in s or "cph_" in s or "time_" in s])
                    cld_angles   =  'selname,' + ','.join([s for s in output if "illum_" in s or "satzen_" in s or "solzen_" in s or "relazi_" in s or "time_" in s])
                    rad_products =  'selname,' + ','.join([s for s in output if "toa_" in s or "boa_" in s or "cla_" in s or "cee_" in s or "time_" in s])
                    if args_l3.local:
                        sat_measurements =  'selname,' + ','.join([s for s in output if "refl_" in s or "bt_" in s or "time_" in s])                   
                    taskfile = open(args_l3.inpdir + "/" + "_".join([args_l3.instrument.upper(), args_l3.satellite.upper(), idnumber, "L3U_splitting_tasklist.txt"]), "w")

                    for path in getdirs:
                        full_path = os.path.join(args_l3.inpdir, path)
                        cd = 'cd ' + full_path
                        files = os.listdir(full_path)
                        for l3u_file in files:
                            if ("CLD_PRODUCTS" in l3u_file and l3u_file.endswith(".nc")):
                                mask = split_l3u(cld_masktype, l3u_file, "CLD_MASKTYPE")
                                ang = split_l3u(cld_angles, l3u_file, "CLD_ANGLES")
                                rad = split_l3u(rad_products, l3u_file, "RAD_PRODUCTS")
                                call = " && ".join([cd, mask, ang, rad])                                
                                if args_l3.local:
                                    toa = split_l3u(sat_measurements, l3u_file, "SAT_MEASUREMENTS")
                                    call = call + " && " + toa
                                prod = split_l3u(cld_products, l3u_file, "CLD_PRODUCTS")
                                call = call + " && " + prod + "\n"
                                taskfile.write(call)
                    taskfile.close()
                    
                    sys.exit(0)

                if args_l3.check_splitting:
                    
                    for root, dirs, files in os.walk(args_l3.inpdir):
                        for name in files:
                            if idnumber in name:
                                taskfile_name = os.path.join(root, name)
                                with open(taskfile_name) as f:
                                    taskfile = f.readlines()
                                    taskfile = [x.strip() for x in taskfile]                                                                
                        for name in dirs:
                            matches = []
                            if name.endswith(idnumber):
                                dirfiles =  os.listdir(os.path.join(root, name))
                                for filename in fnmatch.filter(dirfiles, '*.nc'):
                                    matches.append(filename)
                                nfiles= len(matches)
                                if (nfiles < 4 and not args_l3.local) or (nfiles < 5 and args_l3.local):
                                    print "Not enough NetCDF output files in " + name + ", so will split sequentially"
                                    yyyymmdd = name[0:8]
                                    for line in taskfile:
                                        if yyyymmdd in line:
                                            cwd = line.split()[1]
                                            calls = line.split(" && ")[1:]
                                            for call in calls:
                                                process = sub.Popen(call.split(), stdout=sub.PIPE, stderr=sub.PIPE, cwd=cwd)
                                                output, error = process.communicate()                                                                
                    sys.exit(0)
                        
            # make tarfile
            (tlist, tempdir) = tar_results(args_l3.prodtype.upper(), args_l3.inpdir, 
                                           datestring, sensor, platform, idnumber, args_l3.local)

            logger.info("Copy2ECFS: {0}".format(tlist))
            copy_into_ecfs(datestring, tlist, args_l3.ecfsdir)
            
            logger.info("Move files to {0}".format(tmp_data_storage))
            create_dir(tmp_data_storage)
            move_files(tlist, tmp_data_storage)

            logger.info("Delete \'{0}\'".format(tempdir))
            delete_dir(tempdir)

        else:
            logger.info("Check your input directory, maybe it is empty ?")

    # -- archive now: L3S (sensor family, i.e. all AVHRR or MODIS)
    elif args_l3.prodtype.upper() == "L3S":

        # -- find latest job via ID-US number
        if len(alldirs) > 0:
            getdirs = list()

            # collect right subfolders
            for ad in alldirs:
                if datestring in ad \
                   and args_l3.instrument.upper() in ad \
                   and args_l3.prodtype.upper() in ad \
                   and prodtype_name in ad: 
                    getdirs.append(ad)                    

            # sort list
            getdirs.sort()

            print "________________________________________"
            print getdirs

            # get last element from list, should be last job
            lastdir = getdirs.pop()            

            # get ID number from the last job
            idnumber = get_id(lastdir)

            print "________________________________________"
            print idnumber
            print args_l3.prodtype.upper() + " " +  args_l3.inpdir + " " +  datestring + " " +  sensor + " " + platform + " " + idnumber #+ " " + args_l3.local
            print args_l3.local 

            # make tarfile
            (tlist, tempdir) = tar_results(args_l3.prodtype.upper(), args_l3.inpdir, 
                                           datestring, sensor, platform, idnumber, args_l3.local)
            
            logger.info("Copy2ECFS: {0}".format(tlist))
            copy_into_ecfs(datestring, tlist, args_l3.ecfsdir)
            
            logger.info("Move files to {0}".format(tmp_data_storage))
            create_dir(tmp_data_storage)
            move_files(tlist, tmp_data_storage)

            logger.info("Delete \'{0}\'".format(tempdir))
            delete_dir(tempdir)

        else:
            logger.info("Check your input directory, maybe it is empty ?")

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

    # L3S: only instrument (no platform): sensor family
    parser.add_argument('--satellite', type=str,
                        help='String, e.g. NOAA18')
    #parser.add_argument('--satellite', type=str, required=True,
    #                    help='String, e.g. NOAA18')
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
    l3_parser.add_argument('-loc', '--local', action="store_true",
                           help="Logical, TRUE if set, otherwise FALSE")
    l3_parser.add_argument('--write_l3u_splitlist', action="store_true",
                           help="Logical, TRUE if set, otherwise False")
    l3_parser.add_argument('--check_splitting', action="store_true",
                           help="Logical, TRUE if set, otherwise False")
    l3_parser.add_argument('--proc_toa', type=int, required=True,
                           help="Choices: 0, 1")    
    l3_parser.set_defaults(func=l3)

    # Parse arguments
    args = parser.parse_args()

    # Call function associated with the selected subcommand
    logger.info("*** {0} start for {1}".format(sys.argv[0], args))
    args.func(args)

    logger.info("*** {0:s} succesfully finished \n".format(sys.argv[0]))
