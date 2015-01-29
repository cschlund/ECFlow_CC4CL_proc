#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
# C. Schlundt, December 2014, original version
# C. Schlundt, January 2015, delete config files added
#

import argparse
import os, sys
import shutil
import time, datetime
from housekeeping import delete_dir, get_id
from housekeeping import get_config_file_dict
from housekeeping import delete_file

# -------------------------------------------------------------------
def clear_l1(args):
    '''
    Remove L1 satellite input data if retrieval was successful.
    '''

    # find platform
    if args.satellite.upper() == "TERRA" or \
            args.satellite.upper() == "MOD":
        platform="MOD"
        sensor = "MODIS"

    elif args.satellite.upper() == "AQUA" or \
            args.satellite.upper() == "MYD":
        platform="MYD"
        sensor = "MODIS"

    elif args.satellite.upper().startswith("NOAA"):
        platform=args.satellite.lower()
        sensor = "AVHRR"

    elif args.satellite.upper().startswith("METOP"):
        platform=args.satellite.lower()
        sensor = "AVHRR"

    else:
        print " ! Wrong satellite name !\n"
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
        print (" * No information for cfg filename found in dictionary!")
        print ("   -> Thus, config file cannot be deleted!")

    fname = strlist[1]+strlist[0]+'_'+\
            str(args.year)+'_'+str('%02d' % args.month)+\
            '_'+args.satellite.upper()+strlist[2]

    splitpath = os.path.split( args.inpdir )
    cfgfile   = os.path.join( splitpath[0], strlist[3], fname )

    if os.path.isfile( cfgfile ) == True:
        print ("   - Delete: \'%s\' " % cfgfile)
        delete_file( cfgfile )
    else:
        print ("   - Nothing to delete: \'%s\' does not exist!" 
                % cfgfile ) 



    ipath = os.path.join( args.inpdir, sensor, platform,
            str(args.year), str('%02d' % args.month) )

    if os.path.isdir( ipath ) == True:

        print ("   - Delete: \'%s\' since retrieval was successful!" 
                % ipath)
        delete_dir( ipath )

    else:

        print ("   - Nothing to delete: \'%s\' does not exist!" 
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
        print (" * No information for cfg filename found in dictionary!")
        print ("   -> Thus, config file cannot be deleted!")

    fname = strlist[1]+strlist[0]+'_'+\
            str(args.year)+'_'+str('%02d' % args.month)+\
            '_'+args.satellite.upper()+strlist[2]

    splitpath = os.path.split( args.inpdir )
    cfgfile   = os.path.join( splitpath[0], strlist[3], fname )

    if os.path.isfile( cfgfile ) == True:
        print ("   - Delete: \'%s\' " % cfgfile)
        delete_file( cfgfile )
    else:
        print ("   - Nothing to delete: \'%s\' does not exist!" 
                % cfgfile ) 


    # date string
    datestr = str(args.year)+str('%02d' % args.month)

    # get dirs list containing all subdirs of given path
    alldirs = os.listdir( args.inpdir )

    # if alldirs is not empty
    if len(alldirs) > 0:

        # get dirs list matching the arguments
        getdirs = list()
        for ad in alldirs:
            if datestr in ad \
                    and args.instrument.upper() in ad \
                    and platform in ad and 'retrieval' in ad:
                        getdirs.append( ad )


        # check if getdirs list is empty
        if len(getdirs) == 0:

            print ("   - Nothing to delete in %s for %s %s %s" 
                    % (args.inpdir, args.instrument.upper(),
                        platform, datestr))

        else:

            # sort list
            getdirs.sort()

            # get last element from list, should be last job
            lastdir = getdirs.pop()

            # get ID number from the last job
            id = get_id( lastdir )

            # remove all subdirs matching the id number
            for dir in getdirs:
                if id in dir:
                    delete_dir( dir )

            # pattern
            pattern = datestr+'*'+args.instrument.upper()+'_'+\
                      platform+'_retrieval_'+id

            # remove all dirs matching pattern
            print ('''   - Delete: \'%s\' '''
                   '''because retrieval failed or '''
                   '''was successful!''' % pattern )

    else:

        print ("   - Nothing to delete in %s for %s %s %s" 
                % (args.inpdir, args.instrument.upper(),
                    platform, datestr))

# -------------------------------------------------------------------
def clear_l3(args):
    '''
    Remove L3 results if archiving was successful.
    '''

    # find platform
    if args.satellite.upper() == "TERRA" or \
            args.satellite.upper() == "MOD":
        platform="TERRA"
        sensor = "MODIS"

    elif args.satellite.upper() == "AQUA" or \
            args.satellite.upper() == "MYD":
        platform="AQUA"
        sensor = "MODIS"

    elif args.satellite.upper().startswith("NOAA"):
        platform=args.satellite.upper()
        sensor = "AVHRR"

    elif args.satellite.upper().startswith("METOP"):
        platform=args.satellite.upper()
        sensor = "AVHRR"

    else:
        print " ! Wrong satellite name !\n"
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

    if len(strlist) != 4*numcfgs:
        print (" * No information for cfg filename found in dictionary!")
        print ("   -> Thus, config file cannot be deleted!")

    nc = 0
    while nc < numcfgs:

        cnt = nc * (len(strlist)/numcfgs)
        
        fname = strlist[1+cnt]+strlist[0+cnt]+'_'+\
                str(args.year)+'_'+str('%02d' % args.month)+\
                '_'+args.satellite.upper()+strlist[2+cnt]

        splitpath = os.path.split( os.path.split(args.inpdir)[0] )
        cfgfile   = os.path.join( splitpath[0], strlist[3+cnt], fname )

        if os.path.isfile( cfgfile ) == True:
            print ("   - Delete: \'%s\' " % cfgfile)
            delete_file( cfgfile )
        else:
            print ("   - Nothing to delete: \'%s\' does not exist!" 
                    % cfgfile ) 

        nc += 1


    # date string
    datestr = str(args.year)+str('%02d' % args.month)

    # get dirs list containing all subdirs of given path
    alldirs = os.listdir( args.inpdir )

    if len(alldirs) > 0:

        # get dirs list matching the arguments
        getdirs = list()
        for ad in alldirs:
            if datestr in ad \
                    and sensor in ad \
                    and 'ORAC' in ad \
                    and platform in ad:
                        getdirs.append( ad )

        # check if getdirs list is empty
        if len(getdirs) == 0:

            print ("   - Nothing to delete in %s for %s %s %s" 
                    % (args.inpdir, sensor, platform, datestr))

        else:

            # sort list
            getdirs.sort()

            # get last element from list, should be last job
            lastdir = getdirs.pop()

            # get ID number from the last job
            id = get_id( lastdir )

            # remove all subdirs matching the id number
            for dir in getdirs:
                if id in dir:
                    delete_dir( dir )

            # pattern
            pattern = datestr+'*'+sensor+'_ORAC*'+platform+'*'+id

            # remove all dirs matching pattern
            print ('''   - Delete: \'%s\' '''
                   '''because L2toL3 was successful!''' % pattern )

    else:

        print ("   - Nothing to delete in %s for %s %s %s" 
                % (args.inpdir, sensor, platform, datestr))

# -------------------------------------------------------------------
def clear_aux(args):
    '''
    Remove auxiliary data if complete month was successful.
    '''

    ipath = os.path.join( args.inpdir, args.auxdata )

    if os.path.isdir ( ipath ) == False:
        print ("\n ! The argument for --auxdata should be equal "\
               "to the name of the subfolder you want to clean up.\n")
        sys.exit(0)


    # find corr. config file and delete it
    cfgdict = get_config_file_dict()
    strlist = list()

    if args.auxdata.lower().startswith("aux"):
        auxkey = "aux"
    elif args.auxdata.lower().startswith("era"):
        auxkey = "era"

    for key in cfgdict:
        if "1" in key and auxkey in key:
            strlist.append(key)
            for key2 in cfgdict[key]:
                strlist.append(cfgdict[key][key2])

    if len(strlist) != 4:
        print (" * No information for cfg filename found in dictionary!")
        print ("   -> Thus, config file cannot be deleted!")

    fname = strlist[1]+strlist[0]+'_'+\
            str(args.year)+'_'+str('%02d' % args.month)+strlist[2]

    splitpath = os.path.split( args.inpdir )
    cfgfile   = os.path.join( splitpath[0], strlist[3], fname )

    if os.path.isfile( cfgfile ) == True:
        print ("   - Delete: \'%s\' " % cfgfile)
        delete_file( cfgfile )
    else:
        print ("   - Nothing to delete: \'%s\' does not exist!" 
                % cfgfile ) 


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

            print ("   - Delete: \'%s\' since month was successful!" 
                    % ispath)
            delete_dir( ispath )

        else:

            print ("   - Nothing to delete: \'%s\' does not exist!" 
                    % ispath) 

# -------------------------------------------------------------------


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

    print ("\n *** %s start for %s" % (sys.argv[0], args))

    # Call function associated with the selected subcommand
    args.func(args)

    print (" *** %s succesfully finished \n" % sys.argv[0])

# -------------------------------------------------------------------
