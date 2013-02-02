#!/bin/bash

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   nbMerge - git enabled for Mathematica (R)
#   Stefan Amberger, snambergit@gmail.com
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

# parse arguments

USAGESTRING="./install.sh [path/to/repo] [path/to/nbMerge]"

if [[ "X$1" = "X--help" ]]; then
	echo "usage:"
	echo "$USAGESTRING"
	exit 1
fi

if [[ "X$#" != "X2" ]]; then
	echo "usage:"
	echo "$USAGESTRING"
	exit 1
fi

REPODIR="$1"
NBMERGEDIR="$2"

# check if python is available
if [[ ! -f "/usr/bin/python" ]]; then
	echo "nbMerge needs to find python at \"/usr/bin/python\"."
	exit 1
fi

# sanity check (params need to be directories)
if [[ ! -d "$REPODIR" ]]; then
	echo "Error: $REPODIR does not seem to be a directory."
	exit 1
fi
if [[ ! -d "$NBMERGEDIR" ]]; then
	echo "Error: $NBMERGEDIR does not seem to be a directory."
	exit 1
fi

# save current working directory
CWD=$(pwd)

# change to repository directory to CHECK IF DIRECTORY IS GIT REPO
cd "$REPODIR"

# redirect error stream to /dev/null for next command
exec 2> /dev/null
TOPDIR=$(git rev-parse --show-toplevel)
# redirect error stream to stdout
exec 2>&1

# check if in git repo
if [[ "$TOPDIR" == "" ]]; then
	echo "Error: $REPODIR doesn't seem to be a git repository."
	echo "nbMerge can only be installed in a git repository."
	exit 1
fi

# expand relative math NBMERGEDIR
cd "$CWD"
cd "$NBMERGEDIR"
NBMERGEDIR=$(pwd)

# cd back to where we were
cd $CWD

# check if necessary nbMerge files are present
if [ ! -f "$NBMERGEDIR"/nbMerge/pre-commit-hook-template.sh ];
then
	echo DEBUG "$NBMERGEDIR"/nbMerge/pre-commit-hook-template.sh not found
    echo "Error: nbMerge files not found!"
    echo "Aborting ..."
    exit 2
fi
if [ ! -f "$NBMERGEDIR"/nbMerge/normalize.py ];
then
    echo "Error: nbMerge files not found!"
    echo "Aborting ..."
    exit 3
fi
if [ ! -f "$NBMERGEDIR"/nbMerge/nbMerge.py ];
then
    echo "Error: nbMerge files not found!"
    echo "Aborting ..."
    exit 3
fi

# installing git nbMerge
echo "installing mergetool nbMerge..."
git config --global merge.tool nbMerge
git config --global mergetool.nbMerge.cmd "$NBMERGEDIR/nbMerge/nbMerge.py "'$MERGED'
git config --global mergetool.nbMerge.trustExitCode false

# adding variable containing path of nbmerge directory to pre-commit hook
echo "configuring and copying pre-commit hook ..."
touch "$TOPDIR"/.git/hooks/pre-commit
echo "#!/bin/bash" > "$TOPDIR"/.git/hooks/pre-commit
echo "" >> "$TOPDIR"/.git/hooks/pre-commit
echo 'NBMERGEDIR='"$NBMERGEDIR" >> "$TOPDIR"/.git/hooks/pre-commit
cat "$NBMERGEDIR"/nbMerge/pre-commit-hook-template.sh >> "$TOPDIR"/.git/hooks/pre-commit

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

echo "installation successful"
exit 0
