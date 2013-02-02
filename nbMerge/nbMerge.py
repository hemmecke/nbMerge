#!/usr/bin/python

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

import sys
import os

# returns
#   1   if no conflicts are present
#   2   if part A does not contain a whole cell or does not contain a cell
#   3   if part B does not contain a whole cell or does not contain a cell
def buildMergeNB(data):

	mergeNB = []

	startindices = []
	midindices = []
	endindices = []

	branchA = "branchA"
	branchB = "branchB"

	# find merge conflicts
	lines = data.split('\n')
	for i,line in enumerate(lines):
		if line[:7] == "<<<<<<<":
			# startindices.append(i)
			branchA = line.split()[-1]

		# elif line[:7] == "=======":
			# midindices.append(i)

		elif line[:7] == ">>>>>>>":
			# endindices.append(i)
			branchB = line.split()[-1]
			break

	# find merge conflicts
	hasconflict = data.find("<<<<<<<")
	if hasconflict == -1:
		print 'Error: no conflicts are present.'
		return 1
	else:
		lastConflict = -1
		while True:
			nextConflict = data.find("<<<<<<<",lastConflict+1)
			if nextConflict != -1:
				startindices.append(nextConflict)
				midindices.append(data.find("=======",nextConflict))
				endindices.append(data.find(">>>>>>>",nextConflict))
				lastConflict = nextConflict
			else:
				break

	# number of conflicts
	nconflicts = len(startindices)

	# check that no of conflicts is positive
	if nconflicts == 0:
		print 'Error: no conflicts are present.'
		return 1

	# check if merge conflicts reprecent whole cells, and can
	# thus be processed using this tool
	for i in xrange(nconflicts):
		openingA = data.count('[',startindices[i],midindices[i])
		closingA = data.count(']',startindices[i],midindices[i])
		openingB = data.count('[',midindices[i],endindices[i])
		closingB = data.count(']',midindices[i],endindices[i])

		partAstart = data.find('\n',startindices[i])+1
		partBstart = data.find('\n',midindices[i])+1

		# opening and closing brackets '[' and ']' need to be of same quantity
		# part that is supposed to be merged needs to start with 'Cell['
		if openingA != closingA or data[partAstart:partAstart+5] != 'Cell[':
			print 'Error: part A does not contain a whole cell or does not contain a cell'
			print 'openingA: ',openingA
			print 'closingA: ',closingA
			print 'beginning: ',data[partAstart:partAstart+5]
			return 2
		if openingB != closingB or data[partBstart:partBstart+5] != 'Cell[':
			print 'Error: part B does not contain a whole cell or does not contain a cell'
			print 'openingB: ',openingB
			print 'closingB: ',closingB
			print 'beginning: ',data[partAstart:partAstart+5]
			return 2

	# build merge-notebook
	mergeNB = [data[:startindices[0]]]

	i = 0
	while i < nconflicts:
		# find delimiters of problematic area
		partAstart = data.find('\n',startindices[i])+1
		partAend = midindices[i]-1
		partBstart = data.find('\n',midindices[i])+1
		partBend = endindices[i]-1
		followingPart = data.find('\n', endindices[i])+1

		# add buttons and merge conflicts
		mergeNB.append(neitherButton(i,branchA,branchB)+', ')
		cell = data[partAstart:partAend].strip()
		cell = addCellTag(cell,'nbMerge::'+branchA+' conflict '+str(i))
		mergeNB.append(cell+',')
		mergeNB.append(chooseAButton(i,branchA,branchB)+', ')
		cell = data[partBstart:partBend].strip()
		cell = addCellTag(cell,'nbMerge::'+branchB+' conflict '+str(i))
		mergeNB.append(cell+',')
		mergeNB.append(chooseBButton(i,branchA,branchB))

		# add stuff inbetween conflicts
		if i<nconflicts-1:
			mergeNB.append(data[followingPart:startindices[i+1]])
		i += 1

	# add stuff after last conflict
	footerbegin = data.find('\n',endindices[-1])
	mergeNB.append(data[footerbegin+1:])

	# join lines
	return '\n'.join(mergeNB)


def neitherButton(i,branchA,branchB):
	return 'Cell[BoxData[ButtonBox["\<\\"Choose neither\\"\>", Appearance -> Automatic, ButtonFunction :> (NotebookFind[SelectedNotebook[], "nbMerge::'+branchA+' conflict '+str(i)+'", All, CellTags]; NotebookDelete[SelectedNotebook[]]; NotebookFind[SelectedNotebook[], "nbMerge::'+branchB+' conflict '+str(i)+'", All, CellTags]; NotebookDelete[SelectedNotebook[]]; NotebookFind[SelectedNotebook[], "nbMerge::button'+str(i)+'", All, CellTags]; NotebookDelete[SelectedNotebook[]]), Evaluator -> Automatic, Method -> "Preemptive", BaseStyle->{Smaller, FontFamily -> "Helvetica"}]], "Output", CellTags -> "nbMerge::button'+str(i)+'", ShowCellTags -> False, Background->RGBColor[1, 0.6, 0.6]]'

def chooseAButton(i,branchA,branchB):
	return 'Cell[BoxData[ButtonBox["\<\\"Choose '+branchA+'\\"\>", Appearance -> Automatic, ButtonFunction :> (NotebookFind[SelectedNotebook[], "nbMerge::'+branchB+' conflict '+str(i)+'", All, CellTags]; NotebookDelete[SelectedNotebook[]]; NotebookFind[SelectedNotebook[], "nbMerge::button'+str(i)+'", All, CellTags]; NotebookDelete[SelectedNotebook[]]; SetOptions[ NotebookFind[ SelectedNotebook[], "nbMerge::'+branchA+' conflict '+str(i)+'", All, CellTags], CellTags -> Select[ Flatten[{ReplaceAll[CellTags, Options[ NotebookRead[ SelectedNotebook[]], CellTags]]}], # != "nbMerge::'+branchA+' conflict '+str(i)+'"& ]]), Evaluator -> Automatic, Method -> "Preemptive", BaseStyle->{Smaller, FontFamily -> "Helvetica"}]], "Output", CellTags -> "nbMerge::button'+str(i)+'", ShowCellTags -> False, Background->RGBColor[0.6, 0.8, 1]]'

def chooseBButton(i,branchA,branchB):
	return 'Cell[BoxData[ButtonBox["\<\\"Choose '+branchB+'\\"\>", Appearance -> Automatic, ButtonFunction :> (NotebookFind[SelectedNotebook[], "nbMerge::'+branchA+' conflict '+str(i)+'", All, CellTags]; NotebookDelete[SelectedNotebook[]]; NotebookFind[SelectedNotebook[], "nbMerge::button'+str(i)+'", All, CellTags]; NotebookDelete[SelectedNotebook[]]; SetOptions[ NotebookFind[ SelectedNotebook[], "nbMerge::'+branchB+' conflict '+str(i)+'", All, CellTags], CellTags -> Select[ Flatten[{ReplaceAll[CellTags, Options[ NotebookRead[ SelectedNotebook[]], CellTags]]}], # != "nbMerge::'+branchB+' conflict '+str(i)+'"& ]]), Evaluator -> Automatic, Method -> "Preemptive", BaseStyle->{Smaller, FontFamily -> "Helvetica"}]], "Output", CellTags -> "nbMerge::button'+str(i)+'", ShowCellTags -> False, Background->RGBColor[0.6, 0.8, 1]]'

def addCellTag(cell,tag):

	hasTag = cell.find('CellTags->')
	hasTags = cell.find('CellTags->{')

	newcell = None

	# if cell has no tag
	if hasTag == -1:
		cellend = cell.rfind(']')
		newcell = cell[:cellend]+', CellTags->"'+tag+'", ShowCellTags->True'+cell[cellend:]

	# if cell has one tag
	elif hasTags == -1 and hasTag != -1:
		tagstartpos = cell.find('"',hasTag)
		tagendpos = cell.find('"',tagstartpos+1)

		# show tags
		showtagstring=""
		if cell.find('ShowCellTags') == -1:
			showtagstring=", ShowCellTags->True"

		newcell = cell[:tagstartpos]+'{"'+tag+'",'+cell[tagstartpos:tagendpos]+'"}'+showtagstring+cell[tagendpos+1:]
		newcell = newcell.replace("ShowCellTags->False","ShowCellTags->True")

	# if cell has multiple tags
	elif hasTags != -1:

		openBrace = cell.find('{',hasTags)


		showtagstring = ""
		if cell.find('ShowCellTags') == -1:
			showtagstring=", ShowCellTags->True"

		endtags = cell.find('}',hasTags)
		newcell = cell[:openBrace+1]+'"'+tag+'",'+cell[openBrace+1:endtags+1]+showtagstring+cell[endtags+1:]

	else:
		pass

	return newcell






if __name__ == "__main__" and len(sys.argv) == 2:

	if sys.platform != 'darwin' and sys.platform != 'linux2':
		print "Only operating systems 'darwin' (Mac OS) and 'linux2' (*nix) are supported."
		sys.exit(0)

	filename = sys.argv[1]
	ext = filename.split('.')[-1]

	if ext == "nb":
		print "creating mathematica merge-file"
		inp = open(filename,'r')
		data = inp.read()
		inp.close()

		mergeNB = buildMergeNB(data)
		if mergeNB == 1 or mergeNB == 2 or mergeNB == 3:
			sys.exit(0)

		mergefilename = filename
		out = open(mergefilename,'w')
		out.write(mergeNB)
		out.close()

		if sys.platform == 'darwin':
			os.system('open '+mergefilename)
		else:
			os.system('mathematica '+mergefilename)

	else:
		print "This is not a mathematica notebook file. You probably want to use a different merge-tool."
		sys.exit(0)


# NotebookFind[SelectedNotebook[], "nbMerge::button'+str(i)+'", All, CellTags];