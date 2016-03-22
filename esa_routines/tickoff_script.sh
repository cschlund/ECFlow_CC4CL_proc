#!/usr/bin/env bash

for file in *ksh; do
    echo $file
    /perm/ms/de/sf7/esa_cci_c_proc/routine/tickoff.sh $file > ${file}.to
    mv ${file}.to ${file}
    echo "finished converting file "$file
done

