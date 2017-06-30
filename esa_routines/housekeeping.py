#!/usr/bin/env python2.7

import os
import sys
import fnmatch
import shutil
import re
import tarfile
import subprocess
import datetime
import logging

logger = logging.getLogger('sissi')


def getScriptPath(): 
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def get_file_version():
    """
    Get file_version from config_attributes.file
    """
    try:
        pwd = getScriptPath()
        cfg = os.path.join(pwd, "config_attributes.file")
        fil = open(cfg, "r")
        inp = fil.readlines()
        fil.close()
        for line in inp:
            l = line.strip('\n')
            if 'file_version=' in l:
                splits = l.split("=")
                # remove single quotes from '1.3' and return 1.3
                return splits[1].replace("'", "", 2)
    except IOError:
        logger.info("Could not open file {0}".format(cfg))


def verify_aux_files(file_list):
    """
    Check if files have the right length in order to
    split the filestring correctly.
    """
    for fil in file_list:

        (idir, ifil) = split_filename(fil)
        filebase = os.path.splitext(ifil)[0]

        # MCD43C1.A2008001.005.2008025105553
        # MCD43C3.A2008001.005.2008025111631
        if ifil.startswith('MCD'):
            if len(filebase) != 34:
                file_list.remove(fil)

        # global_emis_inf10_monthFilled_MYD11C3.A2008001.041
        # global_emis_inf10_monthFilled_MYD11C3.A2008001
        elif ifil.startswith('global'):
            if len(filebase) != 46 and len(filebase) != 50:
                file_list.remove(fil)

        # NISE_SSMIF13_20080101 (NISE002 until 20090910)
        # NISE_SSMISF17_20130101 (NISE004 from 20090817)
        elif ifil.startswith('NISE'):
            if len(filebase) != 21 and len(filebase) !=22:
                file_list.remove(fil)

        # ERA_Interim_an_20080101_00+00
        elif ifil.startswith('ERA_Interim'):
            if len(filebase) != 29:
                file_list.remove(fil)

        if 'XXXX' in ifil:
            file_list.remove(fil)

    return file_list


def get_config_file_dict():
    """
    Dictionary containing prefix and suffix of config files.
    cfg_dict["type"]["prefix"]["suffix"]
    """
    cfg_dict = dict()

    type_list = ("1_getdata_aux", "1_getdata_avhrr",
                 "1_getdata_modis", "1_getdata_era",
                 "2_process", "3_make_l3c", "3_make_l3u")

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


def date_from_year_doy(year, doy):
    """
    This function converts the day of year into a datetime object.
    """
    return datetime.datetime(year=year, month=1, day=1) + \
           datetime.timedelta(days=int(doy) - 1)


def split_filename(filename):
    """
    This function splits the full qualified file
    into directory and filename.
    """
    dirn = os.path.dirname(filename)
    base = os.path.basename(filename)
    return dirn, base


def get_file_list_via_pattern(path, pattern):
    """
    This function collects all files in a given
    path which matches the given pattern.
    """
    result = list()
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def get_file_list_via_filext(idir, iend):
    """
    Returns a list of files for a given directory and file
    extension.
    """
    flist = list()
    for root, dirs, files in os.walk(idir):
        for ifile in files:
            if ifile.endswith(iend):
                flist.append(os.path.join(root, ifile))
    flist.sort()
    return flist


def copy_into_ecfs(datestring, file_list, ecfspath):
    """
    Copy tarfile into ECFS archive
    """
    # -- get the right path for ECFS
    ecfs_target = os.path.join(ecfspath, datestring)

    # -- make dir in ECFS
    args = ['emkdir', '-p'] + [ecfs_target]
    logger.info("%s" % args)
    p1 = subprocess.Popen(args, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    stdout, stderr = p1.communicate()
    logger.info("STDOUT:{0}".format(stdout))
    logger.info("STDERR:{0}".format(stderr))

    # -- copy file into ECFS dir
    args = ['ecp', '-o'] + file_list + [ecfs_target]
    logger.info("%s" % args)
    p2 = subprocess.Popen(args, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    stdout, stderr = p2.communicate()
    logger.info("STDOUT:{0}".format(stdout))
    logger.info("STDERR:{0}".format(stderr))

    # -- change mode of files in ECFS
    for fil in file_list:
        filebase = os.path.basename(fil)
        ecfsfile = os.path.join(ecfs_target, filebase)
        args = ['echmod', '555'] + [ecfsfile]
        logger.info(" * %s" % args)
        p3 = subprocess.Popen(args, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        stdout, stderr = p3.communicate()
        logger.info("STDOUT:{0}".format(stdout))
        logger.info("STDERR:{0}".format(stderr))


def tar_results(ptype, inpdir, datestring, sensor, platform, idnumber, local):
    """
    Creates L2, L3U or L3C tarfile.
    """
    # -- check type
    if ptype.upper() == "L3U":
        typ = ptype.upper()
    elif ptype.upper() == "L3C":
        typ = ptype.upper()
    elif ptype.upper() == "L3S":
        typ = ptype.upper()        
    elif ptype.upper() == "L2":
        typ = ptype.upper()
    else:
        logger.info("Wrong type name ! Options: L2, L3U, L3C")
        sys.exit(0)

    print typ 
        
    # -- create tarname
    tarname = create_tarname(typ, datestring, sensor, platform, local)
    print tarname 
    
    # -- define temp. subfolder for tar creation
    if local:
        tempdir = os.path.join(inpdir, "tmp_tardir_" + datestring + "_" + sensor + "_" + platform + "_" + typ.lower() + "_Europe")
    else:
        tempdir = os.path.join(inpdir, "tmp_tardir_" + datestring + "_" + sensor + "_" + platform + "_" + typ.lower())        
    create_dir(tempdir)

    # -- final tarfile to be copied into ECFS
    ecfs_tarfile = os.path.join(tempdir, tarname)
    print ecfs_tarfile
        
    # -- get final tarball
    logger.info("Create \'%s\'" % ecfs_tarfile)
    if typ == "L3U":
        tarfile_list = create_l3u_tarball(inpdir, idnumber,
                                          tempdir, ecfs_tarfile, local, sensor)
    elif typ == "L3C" or typ == "L3S":
        tarfile_list = create_l3c_tarball(inpdir, idnumber,
                                          tempdir, ecfs_tarfile)
    else:
        tarfile_list = create_l2_tarball(inpdir, idnumber,
                                         tempdir, ecfs_tarfile)

    return tarfile_list, tempdir


# noinspection PyUnusedLocal
def create_l2_tarball(inpdir, idnumber, tempdir, l2_tarfile):
    """
    Create the final l2 tarball to be stored in ECFS.
    """
    # -- find l2 input directory via idnumber
    dirs = os.listdir(inpdir)
    daily_list = list()
    if len(dirs) > 0:
        for idir in dirs:
            if idnumber in idir:
                daily_list.append(os.path.join(inpdir, idir))
    else:
        logger.info("No input in {0} matching {1} ".
                format(inpdir, idnumber))
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
        filver = get_file_version()
        suffix = "fv"+filver+".nc"
        files = get_file_list_via_filext(daily, suffix)

        # create daily tarfilename
        ncfile = files.pop()
        ncbase = os.path.splitext(os.path.basename(ncfile))[0]
        nclist = ncbase.split("-")[1:]
        ncstr = "-".join(nclist)
        tarbas = idate + '-' + ncstr
        daily_l2_tarfile = os.path.join(tempdir, tarbas + ".tar")

        # create daily tarfile containing all orbits
        # print (" * Create \'%s\'" % daily_l2_tarfile)
        tar = tarfile.open(daily_l2_tarfile, "w:")
        for tfile in files:
            # filedir = os.path.dirname(tfile)
            filenam = os.path.basename(tfile)
            tar.add(tfile, arcname=filenam)
        tar.close()

        # collect daily tarfiles for final tarball
        tar_file_list.append(daily_l2_tarfile)

    # --------------------------------------------------------
    # NOT POSSIBLE -> larger than 32 GB (limit)
    # --------------------------------------------------------
    # -- make monthly tarballs containing all daily tarballs
    # tar = tarfile.open( l2_tarfile, "w:gz" )
    # for tfile in tar_file_list:
    #    filedir = os.path.dirname(tfile)
    #    filenam = os.path.basename(tfile)
    #    tar.add( tfile, arcname=filenam )
    # tar.close()
    #
    # -- delete daily tarballs
    # for tfile in tar_file_list:
    #    delete_file( tfile )
    # --------------------------------------------------------

    return tar_file_list


def create_l3u_tarball(inpdir, idnumber, tempdir, l3_tarfile, local, sensor):
    """
    Create the final l3u tarball to be stored in ECFS.
    """
    # -- find l3 input directory via idnumber
    if not local:
        split = "." 
        foo = l3_tarfile.split(split)
        foo[-1] = "part1.tar"
        l3_tarfile1 = split.join(foo)
        foo[-1] = "part2.tar"
        l3_tarfile2 = split.join(foo)
        
    dirs = os.listdir(inpdir)
    daily_list = list()
    if len(dirs) > 0:
        for idir in dirs:
            if idnumber in idir and not "splitting_tasklist" in idir:
                nfiles_nc = len( fnmatch.filter(os.listdir(idir), '*.nc'))
                if nfiles_nc ==4:
                    daily_list.append(os.path.join(inpdir, idir))
    else:
        logger.info("No input in {0} matching {1} ".
                format(inpdir, idnumber))
        sys.exit(0)

    # -- final files to be tared
    tar_files = list()

    # -- sort daily list
    daily_list.sort()

    # -- make daily tarballs
    for daily in daily_list:

        # define daily tempdir
        daily_tempdir = os.path.join(tempdir,
                                     daily.split("/")[-1])
        create_dir(daily_tempdir)

        # list of files to be tared
        daily_tar_files = list()

        # list all files
        files = os.listdir(daily)
        for f in files:

            if f.endswith(".nc"):
                # copy file
                source = os.path.join(daily, f)
                if local:
                    index = f.find("-fv")
                    f = f[:index] + "_Europe" + f[index:]
                target = os.path.join(daily_tempdir, f)
                ncbase = os.path.splitext(f)[0]
                shutil.copy2(source, target)

                # add to list
                daily_tar_files.append(target)

            if f.endswith(".tmp"):
                fname, fext = os.path.splitext(f)
                last_folder = daily_tempdir.split("/")[-1]
                # noinspection PyBroadException
                try:
                    pattern = re.search('(.+?)_global',
                                        last_folder).group(1) + '_l2files'
                except:
                    pattern = last_folder + '_l2files'

                # copy file
                l2_tmp = pattern + fext
                source = os.path.join(daily, f)
                target = os.path.join(daily_tempdir, l2_tmp)
                shutil.copy2(source, target)

                # add to list
                daily_tar_files.append(target)

        # create daily tarfile
        ncbase = "-".join([i for i in ncbase.split("-") if "CLD_" not in i and "RAD_" not in i])
        daily_l3_tarfile = os.path.join(tempdir, ncbase + ".tar")
        tar = tarfile.open(daily_l3_tarfile, "w:")
        for tfile in daily_tar_files:
            filenam = os.path.basename(tfile)
            tar.add(tfile, arcname=filenam)
        tar.close()

        # collect daily tarfiles for final tarball
        tar_files.append(daily_l3_tarfile)

        # delete daily_tempdir
        delete_dir(daily_tempdir)

    # -- make monthly tarballs containing all daily tarballs
    if not local:
        tar1 = tarfile.open(l3_tarfile1, "w:")
        tar2 = tarfile.open(l3_tarfile2, "w:")
    else:
        tar = tarfile.open(l3_tarfile, "w:")
    half_tar_files = len(tar_files) / 2
    file_index = 0
    for tfile in tar_files:
        file_index = file_index + 1
        filenam = os.path.basename(tfile)
        if not local: 
            if file_index <= half_tar_files:
                tar1.add(tfile, arcname=filenam)
            else:
                tar2.add(tfile, arcname=filenam)
        else:
            # filedir = os.path.dirname(tfile)
            tar.add(tfile, arcname=filenam)
            
    if not local:
        tar1.close()
        tar2.close()
        return [l3_tarfile1, l3_tarfile2]
    else:
        tar.close()
        return [l3_tarfile]

    # -- delete daily tarballs
    for tfile in tar_files:
        delete_file(tfile)

def create_l3c_tarball(inpdir, idnumber, tempdir, l3_tarfile):
    """
    Create the final l3c tarball to be stored in ECFS.
    """
    # -- find l3c input directory via idnumber
    dirs = os.listdir(inpdir)
    if len(dirs) > 0:
        for idir in dirs:
            if idnumber in idir:
                l3cdir = os.path.join(inpdir, idir)
    else:
        logger.info("No input in {0} matching {1} ".
                format(inpdir, idnumber))
        sys.exit(0)

    # -- list of files to be tared
    tar_files = list()

    # -- list all files
    # noinspection PyUnboundLocalVariable
    files = os.listdir(l3cdir)
    for f in files:

        if f.endswith(".nc"):
            # copy file
            source = os.path.join(l3cdir, f)
            target = os.path.join(tempdir, f)
            shutil.copy2(source, target)

            # add to list
            tar_files.append(target)

        if f.endswith(".tmp"):
            fname, fext = os.path.splitext(f)
            last_folder = l3cdir.split("/")[-1]
            # noinspection PyBroadException
            try:
                pattern = re.search('(.+?)_global',
                                    last_folder).group(1) + '_l2files'
            except:
                pattern = last_folder + '_l2files'

            # copy file
            l2_tmp = pattern + fext
            source = os.path.join(l3cdir, f)
            target = os.path.join(tempdir, l2_tmp)
            shutil.copy2(source, target)

            # add to list
            tar_files.append(target)

    # -- create final tarfile to be copied into ECFS
    tar = tarfile.open(l3_tarfile, "w:")
    for tfile in tar_files:
        filenam = os.path.basename(tfile)
        tar.add(tfile, arcname=filenam)
    tar.close()

    # -- delete input files in temp
    for tfile in tar_files:
        delete_file(tfile)

    return [l3_tarfile]


def split_platform_string(platform):
    """
    Splits platform string into text and number.
    """
    r = re.compile("^([a-zA-Z]+)([0-9]{0,2})$")
    m = r.match(platform)
    return m.group(1), m.group(2)


def create_tarname(ctype, datestring, sensor, platform, local):
    """
    Create tar filename.
    Usage: create_tarname( "L3U", 200806, AVHRR, NOAA18 )
           create_tarname( "L3C", 200806, AVHRR, NOAA18 )
           create_tarname( "L2", 200806, AVHRR, NOAA18 )
    """
    filver = get_file_version()
    esacci = "ESACCI"
    cloudp = "CLOUD-CLD_PRODUCTS"
    if local:
        suffix = "fv"+filver+"_Europe.tar"
    else:
        suffix = "fv"+filver+".tar"
    tarname = datestring + '-' + esacci + '-' + ctype + \
              '_' + cloudp + '-' + sensor + '_' + \
              platform + '-' + suffix
    
    return tarname


def get_id(tmpdir):
    """
    Get ID...US... number from string.
    """
    split = tmpdir.split('_')

    for i in split:
        if i.startswith('ID'):
            id_num = i
        elif i.startswith('US'):
            us_num = i
        else:
            pass

    # noinspection PyUnboundLocalVariable,PyUnboundLocalVariable
    return id_num + '_' + us_num


def move_files(list_of_files, destination):
    """
    Move files to another directory.
    """
    for ifile in list_of_files:
        os.system("mv" + " " + ifile + " " + destination)


def create_dir(tmpdir):
    """
    Create new directory.
    """
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    return tmpdir


def delete_dir(tmpdir):
    """
    Delete non-empty directory.
    """
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)


def delete_file(dfile):
    """
    Delete file.
    Usage: delete_file(/path/to/file.dat)
    """
    if os.path.exists(dfile):
        try:
            os.remove(dfile)
        except OSError, e:
            logger.info("Error: {0} - {1}.".
                    format(e.file, e.strerror))
    else:
        logger.info("Sorry, I can not find {0} file.".
                format(dfile))


def find_file(name, path):
    """
    Find a specific file and return full qualified filename.
    """
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
