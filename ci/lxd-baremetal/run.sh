#!/bin/bash
cd /root/vfscratch-repo
source env.sh
set -e
set -o pipefail
set -u
set +h
set -x
bin/sourcer $vfscratch_build fetch
bin/builder $vfscratch_build $vfscratch_arch $1
