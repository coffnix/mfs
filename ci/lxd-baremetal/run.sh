#!/bin/bash
cd /root/mfs-repo
source env.sh
set -e
set -o pipefail
set -u
set +h
set -x
bin/sourcer $mfs_build fetch
bin/builder $mfs_build $mfs_arch $1
