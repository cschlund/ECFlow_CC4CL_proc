#!/usr/bin/env python2.7

import os, sys
import fnmatch
import shutil
import re, tarfile
import subprocess
import time, datetime

# -------------------------------------------------------------------
def get_config_file_dict():
    """
    Dictionary containing prefix and suffix of config files.
    cfg_dict["type"]["prefix"]["suffix"]
    """
    cfg_dict = dict()

    type_list = ( "1_getdata_aux", "1_getdata_avhrr", 
                  "1_getdata_modis", "1_getdata_era",
                  "2_process", "3_make_l3c", "3_make_l3u" )

    for ctype in type_list:

        cfg_dict[ctype] = dict()

        for add in ("prefix", "suffix", "dir"):

            if add == "prefix": 
                cfg_dict[ctype][add] = "config_proc_"
            elif add == "suffix": 
                cfg_dict[ctype][add] = ".file"
            else:
                cfg_dict[ctype][add] = "temp_cfg_files"

    return cfg_dict


# -------------------------------------------------------------------
def date_from_year_doy(year, doy):
    '''
    This function converts the day of year into 
    a datetime object.
    '''
    return datetime.datetime(year=year, month=1, day=1) + \
            datetime.timedelta(days=int(doy)-1)


# -------------------------------------------------------------------
def split_filename(file):
    '''
    This function splits the full qualified file
    into directory and filename.
    '''
    dirn = os.path.dirname(file)
    base = os.path.basename(file)
    return (dirn, base)


# -------------------------------------------------------------------
def get_file_list_via_pattern( path, pattern ):
    '''
    This function collects all files in a given
    path which matches the given pattern.
    '''
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch( name, pattern ):
                result.append( os.path.join( root, name ) )

    return result


# -------------------------------------------------------------------
def get_file_list_via_filext( idir, iend ):
    """
    Returns a list of files for a given directory and file
    extension.
    """
    flist = list()
    for root, dirs, files in os.walk(idir):
        for file in files:
            if file.endswith(iend):
                flist.append( os.path.join(root,file) )

    flist.sort()
    return flist


# -------------------------------------------------------------------
def copy_into_ecfs(datestring, file_list, ecfspath):
    """
    Copy tarfile into ECFS archive
    """

    # -- get the right path for ECFS
    ecfs_target = os.path.join(ecfspath, datestring)

    # -- make dir in ECFS
    args = ['emkdir', '-p'] + [ecfs_target]
    print (" * %s" % args)
    p1 = subprocess.Popen(args, stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
    stdout, stderr = p1.communicate()
    if p1.returncode > 0:
        print stdout
        print stderr

    # -- copy file into ECFS dir
    args = ['ecp', '-o'] + file_list + [ecfs_target]
    print (" * %s" % args)
    p2 = subprocess.Popen(args, stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
    stdout, stderr = p2.communicate()
    if p2.returncode > 0:
        print stdout
        print stderr

    # -- change mode of files in ECFS
    for fil in file_list: 
        filebase = os.path.basename(fil)
        ecfsfile = os.path.join(ecfs_target, filebase)
        args = ['echmod', '555'] + [ecfsfile]
        print (" * %s" % args)
        p3 = subprocess.Popen(args, stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
        stdout, stderr = p3.communicate()
        if p3.returncode > 0:
            print stdout
            print stderr


# -------------------------------------------------------------------
def tar_results(ptype, inpdir, datestring, sensor, platform, 
        idnumber):
    """
    Creates L2, L3U or L3C tarfile.
    """

    # -- check type
    if ptype.upper() == "L3U":
        typ = ptype.upper()
    elif ptype.upper() == "L3C":
        typ = ptype.upper()
    elif ptype.upper() == "L2":
        typ = ptype.upper()
    else:
        print (" ! Wrong type name ! Options: L2, L3U, L3C")
        sys.exit(0)

    # -- create tarname
    tarname = create_tarname( typ, datestring, sensor, platform ) 
    
    # -- define temp. subfolder for tar creation
    tempdir = os.path.join( inpdir, "tmp_tardir_"+typ.lower() )
    create_dir( tempdir )

    # -- final tarfile to be copied into ECFS
    tarfile = os.path.join( tempdir, tarname)

    # -- get final tarball
    print (" * Create \'%s\'" % tarfile)
    if typ == "L3U":
        tarfile_list = create_l3u_tarball( inpdir, idnumber, 
                                           tempdir, tarfile )
    elif typ == "L3C":
        tarfile_list = create_l3c_tarball( inpdir, idnumber, 
                                           tempdir, tarfile )
    else:
        tarfile_list = create_l2_tarball( inpdir, idnumber, 
                                          tempdir, tarfile )

    return ( tarfile_list, tempdir )


# -------------------------------------------------------------------
def create_l2_tarball( inpdir, idnumber, tempdir, l2_tarfile ):
    """
    Create the final l2 tarball to be stored in ECFS.
    """

    # -- find l2 input directory via idnumber
    dirs = os.listdir( inpdir )
    daily_list = list()
    if len(dirs) > 0:
        for dir in dirs:
            if idnumber in dir: 
                daily_list.append(os.path.join(inpdir,dir))
    else:
        print (" * No input in %s matching %s " % 
                (inpdir, idnumber))
        sys.exit(0)

    # -- final files to be stored in ECFS (daily .tar.gz)
    tar_file_list = list()

    # -- sort daily list
    daily_list.sort()

    # -- make daily tarballs
    for daily in daily_list:

        # date and subdir of daily
        idate_folder = daily.split("/")[-1]
        idate = idate_folder.split("_")[0]

        # list all orbitfiles
        files = get_file_list_via_filext(daily, "fv1.0.nc")

        # create daily tarfilename
        ncfile = files.pop()
        ncbase = os.path.splitext( os.path.basename(ncfile) )[0]
        nclist = ncbase.split("-")[1:]
        ncstr  = "-".join(nclist)
        tarbas = idate + '-' + ncstr
        daily_l2_tarfile = os.path.join(tempdir, tarbas+".tar.gz")

        # create daily tarfile containing all orbits
        #print (" * Create \'%s\'" % daily_l2_tarfile)
        tar = tarfile.open( daily_l2_tarfile, "w:gz" )
        for tfile in files:
            filedir = os.path.dirname(tfile)
            filenam = os.path.basename(tfile)
            tar.add( tfile, arcname=filenam )
        tar.close()

        # collect daily tarfiles for final tarball
        tar_file_list.append( daily_l2_tarfile )

    # --------------------------------------------------------
    # NOT POSSIBLE -> larger than 32 GB (limit)
    # --------------------------------------------------------
    ## -- make monthly tarballs containing all daily tarballs
    #tar = tarfile.open( l2_tarfile, "w:gz" )
    #for tfile in tar_file_list:
    #    filedir = os.path.dirname(tfile)
    #    filenam = os.path.basename(tfile)
    #    tar.add( tfile, arcname=filenam )
    #tar.close()

    ## -- delete daily tarballs
    #for tfile in tar_file_list:
    #    delete_file( tfile )
    # --------------------------------------------------------

    return tar_file_list

# -------------------------------------------------------------------
def create_l3u_tarball( inpdir, idnumber, tempdir, l3_tarfile ):
    """
    Create the final l3u tarball to be stored in ECFS.
    """

    # -- find l3 input directory via idnumber
    dirs = os.listdir( inpdir )
    daily_list = list()
    if len(dirs) > 0:
        for dir in dirs:
            if idnumber in dir: 
                daily_list.append(os.path.join(inpdir,dir))
    else:
        print (" * No input in %s matching %s " % 
                (inpdir, idnumber))
        sys.exit(0)

    # -- final files to be tared
    tar_files = list()

    # -- sort daily list
    daily_list.sort()

    # -- make daily tarballs
    for daily in daily_list:

        # define daily tempdir
        daily_tempdir = os.path.join( tempdir, daily.split("/")[-1] )
        create_dir( daily_tempdir )

        # list of files to be tared
        daily_tar_files = list()

        # list all files
        files = os.listdir(daily)
        for f in files:

            if f.endswith(".nc"):
                # copy file
                source = os.path.join( daily, f )
                target = os.path.join( daily_tempdir, f )
                ncbase = os.path.splitext(f)[0]
                shutil.copy2( source, target )
                
                # add to list
                daily_tar_files.append( target )


            if f.endswith(".tmp"):
                fname, fext = os.path.splitext(f)
                last_folder = daily_tempdir.split("/")[-1]
                try:
                    pattern = re.search( '(.+?)_global',
                              last_folder ).group(1)+'_l2files'
                except:
                    pattern = last_folder+'_l2files'

                # copy file
                l2_tmp = pattern + fext
                source = os.path.join( daily, f )
                target = os.path.join( daily_tempdir, l2_tmp )
                shutil.copy2( source, target )

                # add to list
                daily_tar_files.append( target )


        # create daily tarfile
        daily_l3_tarfile = os.path.join(tempdir, ncbase+".tar.bz2")
        #print (" * Create \'%s\'" % daily_l3_tarfile)

        tar = tarfile.open( daily_l3_tarfile, "w:bz2" )
        for tfile in daily_tar_files:
            filedir = os.path.dirname(tfile)
            filenam = os.path.basename(tfile)
            tar.add(tfile, arcname=filenam)
        tar.close()

        # collect daily tarfiles for final tarball
        tar_files.append( daily_l3_tarfile )

        # delete daily_tempdir
        delete_dir( daily_tempdir )

    # -- make monthly tarballs containing all daily tarballs
    tar = tarfile.open( l3_tarfile, "w:gz" )
    for tfile in tar_files:
        filedir = os.path.dirname(tfile)
        filenam = os.path.basename(tfile)
        tar.add( tfile, arcname=filenam )
    tar.close()

    # -- delete daily tarballs
    for tfile in tar_files:
        delete_file( tfile )

    return [l3_tarfile]


# -------------------------------------------------------------------
def create_l3c_tarball( inpdir, idnumber, tempdir, l3_tarfile ):
    """
    Create the final l3c tarball to be stored in ECFS.
    """

    # -- find l3c input directory via idnumber
    dirs = os.listdir( inpdir )
    if len(dirs) > 0:
        for dir in dirs:
            if idnumber in dir: 
                l3cdir = os.path.join( inpdir, dir )
    else:
        print (" * No input in %s matching %s " % (inpdir, idnumber))
        sys.exit(0)

    # -- list of files to be tared
    tar_files = list()

    # -- list all files
    files = os.listdir( l3cdir )
    for f in files:

        if f.endswith(".nc"):
            # copy file
            source = os.path.join( l3cdir, f)
            target = os.path.join( tempdir, f)
            shutil.copy2( source, target )

            # add to list
            tar_files.append( target )


        if f.endswith(".tmp"):
            fname, fext = os.path.splitext(f)
            last_folder = l3cdir.split("/")[-1]
            try:
                pattern = re.search( '(.+?)_global',
                          last_folder ).group(1)+'_l2files'
            except:
                pattern = last_folder+'_l2files'

            # copy file
            l2_tmp = pattern + fext
            source = os.path.join( l3cdir, f )
            target = os.path.join( tempdir, l2_tmp )
            shutil.copy2( source, target )

            # add to list
            tar_files.append( target )


    # -- create final tarfile to be copied into ECFS
    #print (" * Create \'%s\'" % l3_tarfile)
    tar = tarfile.open( l3_tarfile, "w:gz" )
    for tfile in tar_files:
        filedir = os.path.dirname(tfile)
        filenam = os.path.basename(tfile)
        tar.add(tfile, arcname=filenam)
    tar.close()

    # -- delete input files in temp
    for tfile in tar_files:
        delete_file(tfile)

    return [l3_tarfile]


# -------------------------------------------------------------------
def split_platform_string( platform ):
    """
    Splits platform string into text and number.
    """
    r = re.compile("([a-zA-Z]+)([0-9]+)")
    m = r.match(platform)
    return (m.group(1), m.group(2))


# -------------------------------------------------------------------
def create_tarname( ctype, datestring, sensor, platform ):
    """
    Create tar filename.
    Usage: create_tarname( "L3U", 200806, AVHRR, NOAA18 )
           create_tarname( "L3C", 200806, AVHRR, NOAA18 )
           create_tarname( "L2", 200806, AVHRR, NOAA18 )
    """
    esacci = "ESACCI"
    cloudp = "CLOUD-CLD_PRODUCTS"
    suffix = "fv1.0.tar.gz"

    tarname = datestring + '-' + esacci + '-' + ctype +\
             '_' + cloudp + '-' + sensor + '_' +\
             platform + '-' + suffix

    return tarname


# -------------------------------------------------------------------
def get_id( tmpdir ):
    """
    Get ID...US... number from string.
    """

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
def move_files(list_of_files, destination): 
    """
    Move files to another directory.
    """
    for file in list_of_files: 
        os.system ("mv"+ " " + file + " " + destination) 


# -------------------------------------------------------------------
def create_dir( tmpdir ):
    """
    Create new directory.
    """
    if not os.path.exists( tmpdir ):
        os.makedirs( tmpdir )
    return( tmpdir )


# -------------------------------------------------------------------
def delete_dir( tmpdir ):
    """
    Delete non-empty directory.
    """
    if os.path.exists( tmpdir ):
        shutil.rmtree( tmpdir )


# -------------------------------------------------------------------
def delete_file( file ):
    """
    Delete file.
    Usage: delete_file(/path/to/file.dat)
    """
    if os.path.exists(file): 
        try: 
            os.remove(file) 
        except OSError, e: 
            print (" * Error: %s - %s." % (e.file,e.strerror)) 
    else: 
        print( " * Sorry, I can not find %s file." % file )


# -------------------------------------------------------------------
def find_file(name, path):
    """
    Find a specific file and return full qualified filename.
    """
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

# -------------------------------------------------------------------
