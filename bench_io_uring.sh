#!/usr/bin/env bash

# I'm running the module that is defined in this particular folder,
# this is why pythonpath is defined as the current working directory
PYTHONPATH=$(pwd)

if [[ -z "${1}" ]]; then
    echo "Must provide a name for this run" 1>&2
    exit 1
fi

runtime="${1}"
python3 -m bench_fio --fio-path "/home/jrolon/fio/fio" \
        --target "/dev/nvme0n1" \
        --size 4g \
        --type device \
        --output="/nvme-fio/results/qemu-vfio-user-$(date +%Y_%m_%d_%H_%M_%S)" \
        --mode read write randread randwrite \
        --iodepth 1 2 4 8 16 32 \
        --numjobs 1 2 4 8 16 \
        --engine io_uring \
        --direct 0 \
        --time-based
