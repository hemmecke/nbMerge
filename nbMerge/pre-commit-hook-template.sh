
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
if [ ! -f "$NBMERGEDIR"/nbMerge/normalize.py ];
then
    echo "Error: nbMerge files not found!"
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
	# later recognized by a sed command (see nbMerge-install.sh)
	$NBMERGEDIR/nbMerge/normalize.py $FILE

	if [[ $? -ne 0 ]]; then
		echo "error while processing file $FILE"
		exit 3
	fi

	git add $FILE
done

# If there are whitespace errors, print the offending file names and fail.
git diff-index --check --cached $against --
