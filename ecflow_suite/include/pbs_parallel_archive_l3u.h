#!/usr/bin/env bash

#PBS -N %TASK%
#PBS -q np
#PBS -M dec5@ecmwf.int
#PBS -l EC_hyperthreads=1
#PBS -l EC_threads_per_task=1
#PBS -l EC_memory_per_task=5000mb
#PBS -l EC_total_tasks=%NDAYS_SATDATA%

