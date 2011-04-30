#!/bin/sh

. $(readlink -f $(dirname $0))/../zfsci.conf

mkdir -p $PERSISTENT_PATH/repositories
cd $PERSISTENT_PATH/repositories || exit 1

if [ ! -e behlendorf-spl ]; then
	git clone --mirror git://github.com/behlendorf/spl.git behlendorf-spl
fi

GIT_DIR=behlendorf-spl git fetch

for BRANCH in master; do
	for COMMIT in `GIT_DIR=behlendorf-spl git rev-list --no-merges --max-count=10 $BRANCH`; do
		echo behlendorf-spl $BRANCH $COMMIT
	done
done

exit 0
