#!/usr/bin/env bash

#PBS -N %TASK%
#PBS -q ns
#PBS -M dec5@ecmwf.int
#PBS -l EC_mars=1
#PBS -l EC_total_tasks=1
#PBS -l EC_threads_per_task=1
#PBS -l EC_memory_per_task=1024mb

