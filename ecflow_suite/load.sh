#!/usr/bin/env bash

. config.sh

ecflow_client --load=${SUITE}.def force
ecflow_client --begin=${SUITE}
