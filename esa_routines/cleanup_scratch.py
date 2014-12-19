#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
# C. Schlundt, December 2014
#

import argparse
import os, sys
import shutil
import time, datetime


# -------------------------------------------------------------------
def clear_l1(args):
    '''
    Remove L1 satellite input data if retrieval was successful.
    '''

    # find platform
    if args.satellite.upper() == "TERRA" or \
            args.satellite.upper() == "MOD":
        platform="MOD"

    elif args.satellite.upper() == "AQUA" or \
            args.satellite.upper() == "MYD":
        platform="MYD"

    elif args.satellite.upper().startswith("NOAA"):
        platform=args.satellite.lower()

    elif args.satellite.upper().startswith("METOP"):
        platform=args.satellite.lower()

    else:
        print " ! Wrong satellite name !\n"
        exit(0)


    # find sensor
    if platform == "MOD" or platform == "MYD":
        sensor = "MODIS"
    else:
        sensor = "AVHRR"


    ipath = os.path.join( args.inpdir, sensor, platform,
            str(args.year), str('%02d' % args.month) )

    if os.path.isdir( ipath ) == True:

        print (" *** Delete: \'%s\' since retrieval was successful!" 
                % ipath)
        #delete_dir( ipath )

    else:

        print (" --- Nothing to delete: \'%s\' does not exist!" 
                % ipath) 


# -------------------------------------------------------------------
def clear_l2(args):
    '''
    Search for ID and then remove all directories,
    which belong to this ID and satellite and sensor and date.
    '''
    if args.satellite.upper() == "TERRA":
        platform="TERRA"
    elif args.satellite.upper() == "AQUA":
        platform="AQUA"
    elif args.satellite.upper() == "MOD":
        platform="TERRA"
    elif args.satellite.upper() == "MYD":
        platform="AQUA"
    elif args.satellite.upper().startswith("NOAA"):
        platform=args.satellite.lower()
    elif args.satellite.upper().startswith("METOP"):
        platform=args.satellite.lower()
    else:
        print " ! Wrong satellite name !\n"
        exit(0)

    # date string
    datestr = str(args.year)+str('%02d' % args.month)

    # get dirs list containing all subdirs of given path
    alldirs = os.listdir( args.inpdir )

    if len(alldirs) > 0:

        # get dirs list matching the arguments
        getdirs = list()
        for ad in alldirs:
            if datestr in ad \
                    and args.instrument.upper() in ad \
                    and platform in ad and 'retrieval'in ad:
                        getdirs.append( ad )

        # sort list
        getdirs.sort()

        # get last element from list, should be last job
        lastdir = getdirs.pop()

        # get ID number from the last job
        id = get_id( lastdir )

        ## remove all subdirs matching the id number
        #for dir in getdirs:
        #    if id in dir:
        #        delete_dir( dir )

        # pattern
        pattern = datestr+'*'+args.instrument.upper()+'_'+\
                  platform+'_retrieval_'+id

        # remove all dirs matching pattern
        print (''' *** Delete: \'%s\' '''
               '''because retrieval failed or '''
               '''was successful!''' % pattern )

    else:

        print (" --- Nothing to delete in %s for %s %s %s" 
                % (args.inpdir, args.instrument.upper(),
                    platform, datestr))

# -------------------------------------------------------------------
def clear_l3(args):
    '''
    Remove L3 results if archiving was successful.
    '''

# -------------------------------------------------------------------
def clear_aux(args):
    '''
    Remove auxiliary data if complete month was successful.
    '''

    ipath = os.path.join( args.inpdir, args.auxdata )
    ilist = os.listdir( ipath )

    for i in ilist:

        if i.isdigit() == False: 
            # aux
            ispath = os.path.join( ipath, i, str(args.year), 
                    str('%02d' % args.month) )
        else:
            # ERAinterim
            ispath = os.path.join( ipath, str(args.year), 
                    str('%02d' % args.month) )

        if os.path.isdir( ispath ) == True:

            print (" *** Delete: \'%s\' since month was successful!" 
                    % ispath)
            #delete_dir( ispath )

        else:

            print (" --- Nothing to delete: \'%s\' does not exist!" 
                    % ispath) 

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
def delete_dir( tmpdir ):
    '''
    Deleting non-empty directory.
    '''
    if os.path.exists( tmpdir ):
        shutil.rmtree( tmpdir )

# -------------------------------------------------------------------
# --- main ---
# -------------------------------------------------------------------
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='''
            %s removes directories/files/etc. for given data 
            and date.''' % os.path.basename(__file__))
    
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
            description='''Remove L1 input data if retrieval 
            was successful''')
    clear_l1_parser.add_argument('--satellite', 
            type=str, help="String, e.g. noaa18, TERRA, MYD", 
            required=True)
    clear_l1_parser.add_argument('--instrument', 
            type=str, help="String, e.g. AVHRR, MODIS", 
            required=True)
    clear_l1_parser.set_defaults(func=clear_l1)

    # -> remove retrieval subfolders
    clear_l2_parser = subparsers.add_parser('clear_l2',
            description='''Clean up if retrieval.ecf failed 
            or was successful.''')
    clear_l2_parser.add_argument('--satellite', 
            type=str, help="String, e.g. noaa18, TERRA, MYD", 
            required=True)
    clear_l2_parser.add_argument('--instrument', 
            type=str, help="String, e.g. AVHRR, MODIS", 
            required=True)
    clear_l2_parser.set_defaults(func=clear_l2)

    # -> remove l2tol3 subfolders
    clear_l3_parser = subparsers.add_parser('clear_l3',
            description='''Clean up if l2tol3 failed 
            or was successful.''')
    clear_l3_parser.add_argument('--satellite', 
            type=str, help="String, e.g. noaa18, TERRA, MYD", 
            required=True)
    clear_l3_parser.add_argument('--instrument', 
            type=str, help="String, e.g. AVHRR, MODIS", 
            required=True)
    clear_l3_parser.set_defaults(func=clear_l3)

    # -> remove auxiliary dataset if month was successful
    clear_aux_parser = subparsers.add_parser('clear_aux',
            description='''Remove auxiliary data if month 
            was successfully processed''')
    clear_aux_parser.add_argument('--auxdata', 
            type=str, help="String: e.g. \'aux\', \'ERAinterim\'", 
            required=True)
    clear_aux_parser.set_defaults(func=clear_aux)

    # Parse arguments
    args = parser.parse_args()

    # Call function associated with the selected subcommand
    args.func(args)

# -------------------------------------------------------------------
