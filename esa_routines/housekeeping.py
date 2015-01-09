#!/usr/bin/env python2.7

import os, sys
import shutil
import re, tarfile
import subprocess


# -------------------------------------------------------------------
def copy_into_ecfs(dat, fil):
    """
    Copy tarfile into ECFS archive
    """

    # -- get the right path for ECFS
    ecfs_l3_dir = "ec:/sf7/ESA_Cloud_cci_data/L3"
    ecfs_target = os.path.join(ecfs_l3_dir, dat)

    # -- make dir in ECFS
    #print (" * emkdir -p %s" % ecfs_target)
    p1 = subprocess.Popen(["emkdir", "-p", ecfs_target],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p1.communicate()
    print stdout
    if p1.returncode > 0:
        print stderr

    # -- copy file into ECFS dir
    #print (" * ecp -o %s %s" % (fil, ecfs_target))
    p2 = subprocess.Popen(["ecp", "-o", fil, ecfs_target],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p2.communicate()
    print stdout
    if p2.returncode > 0:
        print stderr

    # -- change mode of file in ECFS
    filebase = os.path.basename(fil)
    #print (" * echmod 555 %s/%s" % (ecfs_target, filebase))
    p3 = subprocess.Popen(["echmod", "555", ecfs_target+"/"+filebase],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p3.communicate()
    print stdout
    if p3.returncode > 0:
        print stderr

    # -- delete file in $SCRATCH
    #print (" * delete %s " % fil)
    delete_file( fil )


# -------------------------------------------------------------------
def tar_l3_results(ptype, inpdir, datestring, 
        sensor, platform, idnumber):
    """
    Creates L3 tarfile, either L3U or L3C.
    """

    # -- check type
    if ptype.upper() == "L3U":
        typ = ptype.upper()
    elif ptype.upper() == "L3C":
        typ = ptype.upper()
    else:
        print (" ! Wrong type name: either \'L3U\' or \'L3C\'")
        sys.exit(0)

    # -- create L3 tarname
    l3_tarname = create_l3_tarname( typ, datestring, 
                                    sensor, platform ) 
    
    # -- define temp. subfolder for tar creation
    tempdir = os.path.join( inpdir, "tmp_tardir_"+typ.lower() )
    create_dir( tempdir )

    # -- final l3 tarfile to be copied into ECFS
    l3_tarfile = os.path.join( tempdir, l3_tarname)

    # -- get final tarball
    print (" * Create \'%s\'" % l3_tarfile)
    if typ == "L3U":
        create_l3u_tarball( inpdir, idnumber, tempdir, l3_tarfile )
    else:
        create_l3c_tarball( inpdir, idnumber, tempdir, l3_tarfile )

    # -- copy tarfile into ECFS
    print (" * Copy2ECFS \'%s\'" % l3_tarfile)
    copy_into_ecfs( datestring, l3_tarfile )

    # -- delete tempdir
    print (" * Delete \'%s\'" % tempdir)
    delete_dir( tempdir )


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
                source = os.path.join( daily, f )
                target = os.path.join( daily_tempdir, f )
                ncbase = os.path.splitext(f)[0]
                #print (" * Copy \'%s\' to \'%s\'" % (source,target))
                shutil.copy2( source, target )
                daily_tar_files.append( target )

            if f.endswith(".tmp"):
                basename    = os.path.splitext(f)[0]
                newsuffix   = ".tar.gz"
                source_file = os.path.join( daily, f)
                target_file = os.path.join( daily_tempdir, basename+newsuffix )
                daily_tar_files.append( target_file )

                #print (" * Create \'%s\'" % target_file)
                tar = tarfile.open( target_file,"w:gz" )
                tar.add( source_file, arcname=f )
                tar.close()

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
            source = os.path.join( l3cdir, f)
            target = os.path.join( tempdir, f)

            #print (" * Copy \'%s\' to \'%s\'" % (source,target))
            shutil.copy2( source, target )
            tar_files.append( target )

        if f.endswith(".tmp"):
            basename    = os.path.splitext(f)[0]
            newsuffix   = ".tar.gz"
            source_file = os.path.join( l3cdir, f )
            target_file = os.path.join( tempdir, basename+newsuffix )
            tar_files.append( target_file )

            #print (" * Create \'%s\'" % target_file)
            tar = tarfile.open(target_file,"w:gz")
            tar.add(source_file, arcname=f)
            tar.close()

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


# -------------------------------------------------------------------
def split_platform_string( platform ):
    """
    Splits platform string into text and number.
    """
    r = re.compile("([a-zA-Z]+)([0-9]+)")
    m = r.match(platform)
    return (m.group(1), m.group(2))


# -------------------------------------------------------------------
def create_l3_tarname( ctype, datestring, sensor, platform ):
    """
    Create tar filename.
    Usage: create_l3_tarnme( "L3U", 200806, AVHRR, NOAA18 )
           create_l3_tarnme( "L3C", 200806, AVHRR, NOAA18 )
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
