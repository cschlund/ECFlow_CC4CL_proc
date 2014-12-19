#!/bin/ksh
#
# Archive l2b and l3 files into the ecfs
#
# Files will be zipped (gzip) and tared
#
# Files that have been already archived will 
# be named (filename).ecfs and not! removed
#
# to remove them use  
# rm_already_archived_L3_files.ksh
#
# written 2012-12-04  St. Stapelberg
# 2013-06-12 Matthias Jerg modifies code. netdf4 with internal compression is now used. gzip only tempfile now.
# 2014-04-08 MJ migration to cca/sf7
# 
# 
############################
#
#          Main
#
############################

set -x 

# source path configfile
. $1

basedir=`pwd`
cd ${l3outputpath}/

set -A dumm `find . -type f -name "*.nc"`

START=$(date +%s)

count=1

for file2cp in ${dumm[*]} ; do

    base=`basename ${file2cp}`
    path=`dirname ${file2cp}`
    tarfile=${path}/`basename ${file2cp} .nc`.tar
    tmpfile=`ls $path/*.tmp`
    datum=`basename ${file2cp} | cut -f1 -d '-'`    #yearmonth[day]
    prodtype=`basename ${file2cp} | cut -f3 -d '-'` #L3U_CLOUD

    if [ ${prodtype} = "L3U_CLOUD" ] ; then
         targetdir=cloud_cci_data/l2b/${datum}
    else
         targetdir=cloud_cci_data/l3/${datum}
    fi

    #make directory for that date in ecfs
    emkdir -p ec:${targetdir}

    # tar and zip it 
    tmpgz=${tmpfile}.gz

    gzip -9 ${tmpfile}

    if [ ${?} -eq 0 ] ; then 

        tar cf ${tarfile} ${file2cp} ${tmpgz} 

        if [ ${?} -eq 0 ] ; then 

            # copy file over into ecfs, set file permissions to "r-x" 
            echo "Copy ${count}/${#dumm[*]}: ${tarfile} ec:${targetdir}" 

            # this first sets the target to overwriteable if it already there 
            echmod 700 ec:${targetdir}/`basename ${tarfile}` 
            ecp -p -t ${tarfile} ec:${targetdir} 

            if [ ${?} -eq 0 ] ; then 

                echmod 555 ec:${targetdir}/`basename ${tarfile}` 
                mv ${file2cp} ${file2cp}".ecfs" 
                mv ${tmpfile} ${tmpfile}".ecfs" 
                rm ${tarfile} 
                echo ${tarfile} " Successfully copied to ecfs!"

            else 

                echo ${tarfile} " ERROR: Copying to ecfs FAILED!"

            fi 

        else 

            echo ${file2cp} "ERROR: Taring FAILED!"

        fi 
    else 

        echo ${tmpfile} "ERROR: Gzipping FAILED!"

    fi

    (( count += 1 ))
done

END=$(date +%s)
DIFF=$(( $END - $START ))
echo "Archiving ${#dumm[*]} File(s) to ecfs took $DIFF seconds"

cd ${basedir}

#end
