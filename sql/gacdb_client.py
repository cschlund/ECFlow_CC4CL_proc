#!/usr/bin/env python

"""Database frontend for the AVHRR GAC archive in ECFS"""

import argparse
import logging

from pycmsaf.avhrr_gac.database import AvhrrGacDatabase
from pycmsaf.argparser import str2date, colon_separated_strings, \
    colon_separated_ints, datetime2pygac
from pycmsaf.logger import setup_root_logger
from pycmsaf.error import error_handler
import pycmsaf


def create(gacdb, args):
    """
    This function is associated with the 'create' subcommand.
    @param gacdb: Database cursor
    @param args: Command line arguments
    """
    # noinspection PyBroadException
    try:
        gacdb.create(ecfs_dir=args.ecfs_dir, overwrite=args.overwrite,
                     years=args.years, test=args.test)
        gacdb.commit_changes()
    except Exception:
        error_handler('Failed to create database')


def sanity_check(gacdb, args):
    """
    This function is associated with the 'sanity_check' subcommand.
    @param gacdb: Database cursor
    @param args: Command line arguments
    """
    # noinspection PyBroadException
    try:
        gacdb.sanity_check(min_size=args.min_file_size,
                           max_length=args.max_length,
                           windowlen=args.windowlen)
        gacdb.commit_changes()
    except Exception:
        error_handler('Failed to perform sanity check')


def get_tarfiles(gacdb, args):
    """
    This function is associated with the 'get_tarfiles' subcommand.
    @param gacdb: Database cursor
    @param args: Command line arguments
    """
    # noinspection PyBroadException
    try:
        tarfiles = gacdb.get_tarfiles(
            start_date=args.start_date,
            end_date=args.end_date,
            sats=args.sats,
            include_blacklisted=args.include_blacklisted,
            order_by_date_time=args.order_by_date_time,
            allow_none=False)

        # Print records to stdout.
        for tarfile in tarfiles:
            print tarfile

    except Exception:
        error_handler('Failed to retrieve tarfiles from the database')


def get_scanlines(gacdb, args):
    """
    This function is associated with the 'get_scanlines' subcommand.
    @param gacdb: Database cursor
    @param args: Command line arguments
    """
    # noinspection PyBroadException
    try:
        # Retrieve Records
        records = gacdb.get_scanlines(satellite=args.sat, date=args.date)

        # Print header if requested
        if args.header:
            if args.mode == 'l1b':
                print "Level 1b Filename | Start-Scanline | End-Scanline"

            else:
                print "Start-Time l1c | End-Time l1c | Start-Scanline | " \
                      "End-Scanline"

        # Print records
        for rec in records:
            if args.mode == 'l1b':
                print ','.join(map(str, [rec['filename'],
                                         rec['start_scanline_endcut'],
                                         rec['end_scanline_endcut']]))
            else:
                print datetime2pygac(rec['start_time_l1c']), \
                    datetime2pygac(rec['end_time_l1c']), \
                    rec['start_scanline_endcut'], \
                    rec['end_scanline_endcut']
    except Exception:
        error_handler('Failed to retrieve scanlines from the database')


def get_sats(gacdb, args):
    """
    This function is associated with the 'get_sats' subcommand.
    @param gacdb: Database cursor
    @param args: Command line arguments
    """
    # noinspection PyBroadException
    try:
        sats = gacdb.get_sats(start_date=args.start_date,
                              end_date=args.end_date, allow_none=False)
    except Exception:
        error_handler('Failed to retrieve satellites from the database')

    for sat in sats:
        print sat


# noinspection PyUnusedLocal
def reset_blacklist(gacdb, args):
    """
    This function is associated with the 'reset_blacklist' subcommand.
    @param gacdb: Database cursor
    @param args: Command line arguments
    """
    # noinspection PyBroadException
    try:
        gacdb.reset_blacklist()
        gacdb.commit_changes()
    except Exception:
        error_handler('Failed to reset blacklist columns.')


# noinspection PyUnusedLocal
def printall(gacdb, args):
    """
    This function is associated with the 'printall' subcommand.
    @param gacdb: Database cursor
    @param args: Command line arguments
    """
    # noinspection PyBroadException
    try:
        gacdb.printall()
    except Exception:
        error_handler('Failed print the database.')


if __name__ == '__main__':
    # Setup logger
    logger = setup_root_logger(
        name='gacdb_client', loglevel=logging.INFO)
    pycmsaf.set_loglevel(logging.DEBUG)

    # Setup argument parser
    parser = argparse.ArgumentParser(description='Database frontend for the '
                                                 'AVHRR GAC archive in ECFS')

    # Add main arguments
    parser.add_argument('--dbfile', type=str, required=True,
                        help='Specifies the database file.')

    # Define subcommands
    subparsers = parser.add_subparsers(help='Select a Subcommand')

    # -> create
    create_parser = subparsers.add_parser(
        'create', description='Create database from ECFS contents.')
    create_parser.add_argument('--ecfs_dir', type=str, required=True,
                               help='ECFS directory holding AVHRR GAC data.')
    create_parser.add_argument('--overwrite', action='store_true',
                               help='Overwrite existing database file.')
    create_parser.add_argument('--years', type=colon_separated_ints,
                               help='Only store data within these years. '
                                    'Expected Format: year1,year2,....')
    create_parser.add_argument('--test', action='store_true',
                               help='Test mode on local workstation.')
    create_parser.set_defaults(func=create)

    # -> sanity_check
    sanity_parser = subparsers.add_parser(
        'sanity_check', description='Perform sanity check on all records in the'
                                    'database. Records failing the test will '
                                    'be blacklisted.')
    sanity_parser.add_argument('--min_file_size', type=int, default=7864320.0,
                               help='Minimum allowed l1b file size in bytes.')
    sanity_parser.add_argument('--max_length', type=int, default=120,
                               help='Maximum allowed orbit length in minutes.')
    sanity_parser.add_argument('--windowlen', type=int, default=20,
                               help='Determines the size of a record\'s '
                                    'neighbourhood to be searched for '
                                    'redundant orbits.')
    sanity_parser.set_defaults(func=sanity_check)

    # -> get_tarfiles
    get_tar_parser = subparsers.add_parser(
        'get_tarfiles',
        description='Retrieve tar archive names from the database. '
                    'By default all tarfiles in the database are returned. '
                    'You may restrict the returned results by specifying a '
                    'date interval and satellite name(s).')
    get_tar_parser.add_argument(
        '--start_date', type=str2date,
        help='Only retrieve records whose corresponding orbit start date is '
             '>= the given date. Expected Format: yyyymmdd .')
    get_tar_parser.add_argument(
        '--end_date', type=str2date,
        help='Only retrieve records whose corresponding orbit start date '
             'is <= the given date. Expected Format: yyyymmdd .')
    get_tar_parser.add_argument('--sats', type=colon_separated_strings,
                                help='Only retrieve records matching the given '
                                     'satellites (separated by colons).')
    get_tar_parser.add_argument('--include_blacklisted', action='store_true',
                                help='Include blacklisted records.')
    get_tar_parser.add_argument('--order_by_date_time', action='store_true',
                                help='Order tarfiles by date & time instead of '
                                     'ordering them by optimal ECFS-retrieval '
                                     'order.')
    get_tar_parser.set_defaults(func=get_tarfiles)

    # -> get_scanlines
    scanline_parser = subparsers.add_parser(
        'get_scanlines',
        description='Retrieve all orbits from the database which contain data '
                    'of the given date and satellite. For each of them, '
                    'determine the scanlines to be processed to obtain an '
                    'overlap-free coverage of the day. Results are printed to '
                    'stdout.')
    scanline_parser.add_argument('--date', type=str2date, required=True,
                                 help='Specifies the date to be processed.')
    scanline_parser.add_argument('--sat', type=str, required=True,
                                 help='Specifies the satellite name.')
    scanline_parser.add_argument('--mode', type=str, choices=('l1b', 'l1c'),
                                 required=True,
                                 help='Specifies whether the selection should '
                                      'be done based on l1b or l1c timestamps.')
    scanline_parser.add_argument('--header', action='store_true',
                                 help='Print header explaining the columns.')
    scanline_parser.set_defaults(func=get_scanlines)

    # -> get_sats
    get_sats_parser = subparsers.add_parser(
        'get_sats',
        description='Retrieve a unique set of satellites available in a given '
                    'time period.')
    get_sats_parser.add_argument('--start_date', type=str2date,
                                 help='Specifies the start date of the time '
                                      'period to be searched.')
    get_sats_parser.add_argument('--end_date', type=str2date,
                                 help='Specifies the end date of the time '
                                      'period to be searched.')
    get_sats_parser.set_defaults(func=get_sats)

    # -> reset_blacklist
    reset_parser = subparsers.add_parser(
        'reset_blacklist', description='Reset all blacklist columns.')
    reset_parser.set_defaults(func=reset_blacklist)

    # -> prinall
    print_parser = subparsers.add_parser(
        'printall', description='Print all records in the database')
    print_parser.set_defaults(func=printall)

    # Parse arguments
    args = parser.parse_args()

    # Create GacDatabase instance
    gacdb = AvhrrGacDatabase(dbfile=args.dbfile)

    # Call function associated with the selected subcommand
    args.func(gacdb, args)

