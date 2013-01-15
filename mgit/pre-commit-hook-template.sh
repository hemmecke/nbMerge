#!/bin/bash

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   mgit - git enabled for Mathematica (R)
#   Stefan Amberger, amberger.stefan@gmail.com
#
#   Copyright (2013) Stefan Amberger. This software is distributed under
#   the GNUv3 General Public License.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# redirect error stream to /dev/null for next command
exec 2> /dev/null

TOPDIR=$(git rev-parse --show-toplevel)

# redirect error stream to stdout
exec 2>&1

# check if in git repo
if [[ "$TOPDIR" == "" ]]; then
	echo "Error: You don't seem to be in a git repository."
	echo "mgit can only be installed in a git repository."
	exit 1
fi

# check if necessary mgit files are present
if [ ! -f "$TOPDIR"/mgit/normalize.py ];
then
    echo "Error: mgit files not found!"
    echo "Aborting ..."
    exit 2
fi

if git rev-parse --verify HEAD >/dev/null 2>&1
then
	against=HEAD
else
	# Initial commit: diff against an empty tree object
	against=4b825dc642cb6eb9a060e54bf8d69288fbee4904
fi

FILES="$(git diff --cached --name-only $against)"
echo "files:"
echo "$FILES"

for FILE in $FILES; do
	# do not add a '$' here!! this is not a variable, but a substitution-pattern
	# later recognized by a sed command (see mgit-install.sh)
	python $TOPDIR/mgit/normalize.py $FILE

	if [[ $? -ne 0 ]]; then
		echo "error while processing file $FILE"
		exit 3
	fi

	git add $FILE
done

# If there are whitespace errors, print the offending file names and fail.
git diff-index --check --cached $against --