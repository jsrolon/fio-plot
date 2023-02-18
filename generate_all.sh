#!/usr/bin/env bash

declare -a paths=("qemu-dummy-nvme-2022_05_27_14_40_54/nvme0n1/libaio" "host-spdk-2022_05_20_14_21_06/trtype=PCIe traddr=0000.bc.00.0 ns=1/spdk" "qemu-hostdev-igb_uio-2022_05_19_14_02_35/trtype=PCIe traddr=0000.06.00.0 ns=1/spdk" "qemu-vfio-user-igb_uio-2022_05_19_00_50_59/trtype=PCIe traddr=0000.00.02.0 ns=1/spdk")

for i in "${paths[@]}"; do
  venv/bin/python3 -m fio_plot --input-directory "/Users/jsrolon/nvme-fio/results/${i}/4k" \
    --title "Test" \
    --latency-iops-2d-nj \
    --rw randwrite \
    --numjobs 1 2 4 8 16 \
    --iodepth 1 2 4 8 16
done
