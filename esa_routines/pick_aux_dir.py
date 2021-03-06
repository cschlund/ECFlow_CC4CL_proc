#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
# C. Schlundt, November 2014
#

import argparse
import os
import sys
import datetime
import time
import numpy

from pycmsaf.logger import setup_root_logger

from housekeeping import get_file_list_via_pattern
from housekeeping import split_filename
from housekeeping import date_from_year_doy
from housekeeping import verify_aux_files

logger = setup_root_logger(name='sissi')


def find_nearest_date(args_pick):
    """
    Find the nearest auxiliary data for current processing month.
    :param args_pick: command line arguments
    :return: String (full qualified file)
    """
    # logger.info("Find Auxiliary File for: {0}".format(args_pick))

    # reference date
    ref_date = datetime.datetime(args_pick.year, args_pick.month,
                                 args_pick.day, args_pick.hour,
                                 args_pick.minute, args_pick.seconds)

    # all logger info containing args_pick because retrieval logfile
    # is a bit chaotic due to wrapper (aprun, parallel mode)

    # scratch is a bitch, thus try several times in case of scratch issues
    tryno = 10
    tryno_range = range(1,tryno+1,1)

    for t in tryno_range:
        # logger.info("Get file list")
        if 'ERAinterim' in args_pick.inpdir \
                or 'ERA_Interim' in args_pick.inpdir: 
            file_list = get_file_list_via_pattern(args_pick.inpdir, 
                                                  '*.' + args_pick.suffix)
        else:
            ystr = str(args_pick.year)
            mstr = str(args_pick.month).zfill(2)
            search_path = os.path.join(args_pick.inpdir, ystr, mstr)
            file_list = get_file_list_via_pattern(search_path, 
                                                  '*.' + args_pick.suffix)

        if len(file_list) == 0:
            if t < tryno: 
                # logger.info("{0}.TRY: No file list returned, "
                #             "sleep a bit".format(t))
                time.sleep(numpy.random.randint(1, 20))
                continue
            else:
                # logger.info("Are you sure that you are searching "
                #             "in the right path?")
                sys.exit(0)
        else: 
            # logger.info("Sort file list")
            file_list.sort()
            # logger.info("Verify file list")
            verified_file_list = verify_aux_files(file_list)

            if len(verified_file_list) > 0:
                # logger.info("Get date list")
                dates = map(extract_date, verified_file_list)
                # logger.info("Get date_diff list")
                diffs = map(lambda x: abs((x - ref_date).total_seconds()), dates)
                # logger.info("Now grep nearest date")
                min_val = min(diffs)
                min_idx = diffs.index(min_val)
                return verified_file_list[min_idx]
            else:
                # logger.info("Verified file list is empty! "
                #             "Check if input data are really available!")
                sys.exit(0)


def extract_date(ifile):
    """
    This function receives a full qualified file and
    returns the date contained in the filename as datetime object.
    """

    global dt
    (idir, fil) = split_filename(ifile)

    # MCD43C1.A2008001.005.2008025105553.hdf
    # MCD43C3.A2008001.005.2008025111631.hdf
    if fil.startswith('MCD'):
        fsplit = fil.split('.')
        for s in fsplit:
            if s.startswith('A'):
                ss = s.replace("A", "")
                dt = date_from_year_doy(int(ss[:-3]),
                                        int(ss[4:]))

    # global_emis_inf10_monthFilled_MYD11C3.A2008001.041.nc
    # global_emis_inf10_monthFilled_MYD11C3.A2008001.nc
    elif fil.startswith('global'):
        fbasen = os.path.splitext(fil)
        fsplit = fbasen[0].split('.')
        for s in fsplit:
            if s.startswith('A'):
                ss = s.replace("A", "")
                dt = date_from_year_doy(int(ss[:-3]),
                                        int(ss[4:]))

    # NISE_SSMIF13_20080101.HDFEOS
    elif fil.startswith('NISE'):
        fbasen = os.path.splitext(fil)
        fsplit = fbasen[0].split('_')
        dt = datetime.datetime(int(fsplit[2][:-4]),
                               int(fsplit[2][4:-2]),
                               int(fsplit[2][6:]))

    # ERA_Interim_an_20080101_00+00.nc
    elif fil.startswith('ERA_Interim'):
        fbasen = os.path.splitext(fil)
        fsplit = fbasen[0].split('_')
        fstime = fsplit[4].split('+')
        dt = datetime.datetime(int(fsplit[3][:-4]),
                               int(fsplit[3][4:-2]),
                               int(fsplit[3][6:]),
                               int(fstime[0]),
                               int(fstime[1]))
    return dt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''
            %s searches for nearest auxiliary data available
            for given date.''' % os.path.basename(__file__))

    # add main arguments (for aux data)
    parser.add_argument('--inpdir', type=str, required=True,
                        help="String, e.g. /path/to/aux/file.suffix")
    parser.add_argument('--suffix', type=str, required=True,
                        help="String, e.g. hdf")
    parser.add_argument('--year', type=int,
                        help="Integer, e.g. 2010", required=True)
    parser.add_argument('--month', type=int,
                        help="Integer, e.g. 1", required=True)
    parser.add_argument('--day', type=int,
                        help="Integer, e.g. 1", required=True)
    parser.add_argument('--hour', type=int, default=0,
                        help="Integer, e.g. 1")
    parser.add_argument('--minute', type=int, default=0,
                        help="Integer, e.g. 1")
    parser.add_argument('--seconds', type=int, default=0,
                        help="Integer, e.g. 1")
    parser.set_defaults(func=find_nearest_date)

    # Parse arguments
    args = parser.parse_args()

    # Call function associated with the selected subcommand
    mfile = args.func(args)
    print mfile
    #logger.info("PICK_AUX_RETURN:{0}".format(mfile))
