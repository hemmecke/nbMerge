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
if [ ! -f "$TOPDIR"/mgit/pre-commit-hook-template.sh ];
then
    echo "Error: mgit files not found!"
    echo "Aborting ..."
    exit 2
fi
if [ ! -f "$TOPDIR"/mgit/normalize.py ];
then
    echo "Error: mgit files not found!"
    echo "Aborting ..."
    exit 3
fi

echo "configuring and copying pre-commit hook ..."
cp "$TOPDIR"/mgit/pre-commit-hook-template.sh "$TOPDIR"/.git/hooks/pre-commit
if [[ $? -ne 0 ]]; then
	echo "An error occurred while configuring or copying the pre-commit hook."
	echo "Please check file './.git/hooks/pre-commit' and remove it if necessary."
	exit 4
fi

echo "setting execute-bits of pre-commit hook ..."
chmod +x "$TOPDIR"/.git/hooks/pre-commit
if [[ $? -ne 0 ]]; then
	echo "An error occurred in changing the file mode of './.git/hooks/pre-commit'."
	echo "Please run the command 'chmod +x ./.git/hooks/pre-commit' manually."
	exit 5
fi

echo "customizing mgit_skeleton.py ..."
touch "$TOPDIR"/mgit/mgit
echo '#!'$(which python) > "$TOPDIR"/mgit/mgit
cat "$TOPDIR"/mgit/mgit_skeleton.py >> "$TOPDIR"/mgit/mgit
chmod +x "$TOPDIR"/mgit/mgit

echo "installation successful"