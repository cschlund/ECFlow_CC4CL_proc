#!/usr/bin/env python2.7

import os
from os.path import join as pjoin
import sys
import argparse
import datetime
import shutil
import fnmatch

from pycmsaf.avhrr_gac.database import AvhrrGacDatabase
from pycmsaf.argparser import datetime2pygac

def get_file_list_via_pattern(path, pattern):
    """
    This function collects all files in a given
    path which matches the given pattern.
    """
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                return os.path.join(root, name)

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print 'Usage: python list_daily_orbits.py <dbfile> <current date as yyyymmdd> '\
              '<satellite> <l1 input directory> <file type [avhrr, sunsat, qual]>'
        sys.exit(1)

    dbfile            = sys.argv[1]
    current_date_str   = sys.argv[2]
    satellite         = sys.argv[3].upper()
    l1_base_directory = sys.argv[4]
    ftype = sys.argv[5]

    # create datetime instance of current date
    date_fmt = '%Y%m%d'
    current_date = datetime.datetime.strptime(current_date_str, date_fmt).date()

    # create date for previous day
    previous_date = current_date - datetime.timedelta(days=1)

    # Compose paths
    l1_dir_current_day = pjoin(l1_base_directory, 
                               current_date.strftime('%Y'),
                               current_date.strftime('%m'),
                               current_date.strftime('%d'),
                               current_date.strftime('%Y%m%d'))
    l1_dir_previous_day = pjoin(l1_base_directory,
                                previous_date.strftime('%Y'),
                                previous_date.strftime('%m'),
                                previous_date.strftime('%d'),
                                previous_date.strftime('%Y%m%d'))

    # List directory contents
    l1_files_current_day = [pjoin(l1_dir_current_day, fname) 
                            for fname in os.listdir(l1_dir_current_day)]
    
    # Connect to database
    db = AvhrrGacDatabase(dbfile=dbfile)

    # Retrieve orbits & scanlines associated with current date
    records = db.get_scanlines(satellite=satellite, date=current_date)

    for rec in records:

        fname_dst = None

        # Compose datetime string as created by pygac
        tstart = datetime2pygac(rec['start_time_l1c'])

        path = l1_dir_current_day
        pattern = "ECC_GAC_" + ftype + "*_" + tstart + "_*"

        # Search for corresponding l1c file
        if rec['start_time_l1c'].date() == previous_date and not current_date.day == 1:
            l1_files_previous_day = [pjoin(l1_dir_previous_day, fname)
                                     for fname in os.listdir(l1_dir_previous_day)]
            fname_src = get_file_list_via_pattern(path, pattern)
            fname_dst = pjoin(l1_dir_current_day, os.path.basename(fname_src))

            # Copy file to the current day's input directory
            checkFile = os.path.isfile(fname_dst)
            if not checkFile:
                shutil.copy(src=fname_src, dst=fname_dst)
        if rec['start_time_l1c'].date() == current_date:
            fname_dst = get_file_list_via_pattern(path, pattern)

        if fname_dst:
            if ftype == "avhrr":
                print fname_dst, rec['start_scanline_endcut'], rec['end_scanline_endcut'], rec['across_track']
            else:
                print fname_dst

        print
