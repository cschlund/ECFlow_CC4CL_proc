#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
# C. Schlundt, November 2014
#

import argparse
import os
import datetime

from housekeeping import get_file_list_via_pattern
from housekeeping import split_filename
from housekeeping import date_from_year_doy


def find_nearest_date(args_pick):
    """
    Find the nearest auxiliary data for current processing month.
    :param args_pick: command line arguments
    :return: String (full qualified file)
    """
    # reference date
    ref_date = datetime.datetime(args_pick.year, args_pick.month,
                                 args_pick.day, args_pick.hour,
                                 args_pick.minute, args_pick.seconds)

    # get file list
    files = get_file_list_via_pattern(args_pick.inpdir, '*.' + args_pick.suffix)
    files.sort()

    # remove climatology files
    # climatology_files = [f for f in files if 'XXXX' in f]
    # for i in climatology_files:
    #    files.remove(i)

    # get date list
    dates = map(extract_date, files)

    # get diffs list
    diffs = map(lambda x: abs((x - ref_date).total_seconds()), dates)

    # grep nearest date
    min_val = min(diffs)
    min_idx = diffs.index(min_val)

    return files[min_idx]


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

    # ERA_Interim_an_20080101_00+00.grb
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