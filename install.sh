#!/bin/bash

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   nbMerge - git enabled for Mathematica (R)
#   Stefan Amberger, amberger.stefan@gmail.com
#
#   Copyright (2013) Stefan Amberger. This software is distributed under
#   the GNU General Public License.
#
#   This file is part of nbMerge.
#
#   nbMerge is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   nbMerge is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with nbMerge.  If not, see <http://www.gnu.org/licenses/>.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# redirect error stream to /dev/null for next command
exec 2> /dev/null

TOPDIR=$(git rev-parse --show-toplevel)

# redirect error stream to stdout
exec 2>&1

# check if in git repo
if [[ "$TOPDIR" == "" ]]; then
	echo "Error: You don't seem to be in a git repository."
	echo "nbMerge can only be installed in a git repository."
	exit 1
fi

# check if necessary nbMerge files are present
if [ ! -f "$TOPDIR"/nbMerge/pre-commit-hook-template.sh ];
then
    echo "Error: nbMerge files not found!"
    echo "Aborting ..."
    exit 2
fi
if [ ! -f "$TOPDIR"/nbMerge/normalize.py ];
then
    echo "Error: nbMerge files not found!"
    echo "Aborting ..."
    exit 3
fi

echo "configuring and copying pre-commit hook ..."
cp "$TOPDIR"/nbMerge/pre-commit-hook-template.sh "$TOPDIR"/.git/hooks/pre-commit
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

echo "customizing nbMerge_skeleton.py ..."
touch "$TOPDIR"/nbMerge/nbMerge
# echo '#!'$(which python) > "$TOPDIR"/nbMerge/nbMerge
cat "$TOPDIR"/nbMerge/nbMerge_skeleton.py >> "$TOPDIR"/nbMerge/nbMerge
chmod +x "$TOPDIR"/nbMerge/nbMerge

echo "installation successful"