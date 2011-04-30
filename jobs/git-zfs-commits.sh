#!/bin/sh

. $(readlink -f $(dirname $0))/../zfsci.conf

mkdir -p $PERSISTENT_PATH/repositories
cd $PERSISTENT_PATH/repositories || exit 1

if [ ! -e behlendorf-zfs ]; then
	git clone --mirror git://github.com/behlendorf/zfs.git behlendorf-zfs
fi

GIT_DIR=behlendorf-zfs git fetch

for BRANCH in master; do
	for COMMIT in `GIT_DIR=behlendorf-zfs git rev-list --no-merges --max-count=10 $BRANCH`; do
		echo behlendorf-zfs $BRANCH $COMMIT
	done
done

exit 0
