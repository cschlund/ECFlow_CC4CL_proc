#!/usr/bin/env python

import os
import time
import argparse
from datetime import datetime, timedelta
from stat import *

# -- parser arguments

parser = argparse.ArgumentParser(
    description=u'''{0:s} looks for files older than args.days
    and modifies time stamp to current date. '''.format(
        os.path.basename(__file__)))

parser.add_argument('-i', '--inpdir', required=True, type=str,
                    help='Path to files to be checked/modified.')

parser.add_argument('-e', '--extension', required=True, type=str,
                    help='File extension of files to be checked/modified.')

parser.add_argument('-d', '--days', required=True, type=int,
                    help='Today minus days = check files older than this date.')

args = parser.parse_args()

# current time stamp
cur_date = datetime.now()
# max date in the past
max_date = cur_date + timedelta(days=-args.days)

print " *** Current date               : {0}".format(cur_date)
print " *** Search for files older than: {0}".format(max_date)

# returns a list of all the files on the current directory
flist = list()
for root, dirs, files in os.walk(args.inpdir):
    for ifile in files:
        if ifile.endswith(args.extension):
            flist.append(os.path.join(root, ifile))
flist.sort()

# list of older files
olist = list()

# loop over files
for ff in flist:

    # actual time stamp of file
    fil_date = datetime.fromtimestamp(os.path.getmtime(ff))

    if fil_date < max_date:

        olist.append(ff)
        print ("   -> OLD %s: %s" % (ff, fil_date))

        if ff.endswith(args.extension):
            # get time stamp information
            st = os.stat(ff)
            atime = st[ST_ATIME]  # access time
            mtime = st[ST_MTIME]  # modification time

            # actual unixtime
            cur_unix = time.mktime(cur_date.timetuple())
            # cur_pyth = datetime.fromtimestamp( int( cur_unix ) )

            # new modification time
            new_mtime = cur_unix

            # modify the file timestamp 
            os.utime(ff, (atime, new_mtime))
            new_date = datetime.fromtimestamp(os.path.getmtime(ff))
            print ("   -> NEW %s: %s\n" % (ff, new_date))

            # else:
            #    print (" * OK %s: %s" % (ff, fil_date))

print " *** {0} were older than {1} ".format(len(olist), max_date)
