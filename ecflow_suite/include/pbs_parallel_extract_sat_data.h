#!/usr/bin/env bash

#PBS -N %TASK%
#PBS -q np
#PBS -l EC_ecfs=0
#PBS -l EC_mars=0
#PBS -M dec5@ecmwf.int
#PBS -l walltime=02:00:00
#PBS -l EC_total_tasks=%NDAYS_SATDATA%
#PBS -l EC_tasks_per_node=16
#PBS -l EC_memory_per_task=3000mb
#PBS -l EC_threads_per_task=1
#PBS -l EC_hyperthreads=1

