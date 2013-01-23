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

import sys

### NORMALIZATION 1 - PUT ALL EXPRESSIONS THAT START WITH expr INTO ONE LINE
def removeNLinExpr(data,expr):
	lexpr = len(expr)
	bracketcount_of_expr = expr.count('[')

	count = data.count(expr)

	# find indices of start of expr
	startCellIndices = []
	found = data.find(expr)
	if found == -1:
		return data
		# return data
	else:
		startCellIndices = [found]
	for i in xrange(0,count):
		start = data.find(expr,startCellIndices[-1]+1)
		if start != -1:
			startCellIndices.append(start)

	# find first closing bracket for each hit
	len_startCellIndices = len(startCellIndices)
	endCellIndices = []
	for ind in startCellIndices:
		openBrackets = bracketcount_of_expr
		position = ind + lexpr
		# print 'starting at index: ',position
		while openBrackets>0:
			char = data[position]
			if char == ']':
				# print 'char: ',char
				openBrackets -= 1
			elif char == '[':
				openBrackets += 1
				# print 'char: ',char
			else:
				pass
				# print 'char: ',char
			position += 1
			# print 'open brackets: ',openBrackets

		endCellIndices.append(position)

	# check for overlapping Cells
	# and remove the inner cells from the list
	filteredStartCellIndices = []
	filteredEndCellIndices = []

	# print 'startCellIndices: ',startCellIndices
	# print 'endCellIndices: ',endCellIndices

	maxEndInd = 0
	i = 0
	while i<len_startCellIndices:
		if endCellIndices[i] > maxEndInd:
			filteredStartCellIndices.append(startCellIndices[i])
			filteredEndCellIndices.append(endCellIndices[i])
			maxEndInd = endCellIndices[i]
		i += 1

	# print 'filteredStartCellIndices: ',filteredStartCellIndices
	# print 'filteredEndCellIndices: ',filteredEndCellIndices

	# remove newlines from within the ranges start:end
	newdata = []
	# add stuff before first cell
	newdata.append(data[:filteredStartCellIndices[0]]+'\n')
	for i in xrange(len(filteredStartCellIndices)):
		# add cell
		nonewline = ' '.join(data[filteredStartCellIndices[i]:filteredEndCellIndices[i]].split('\n'))
		newdata.append(nonewline)
		# add stuff between cells
		if i<len(filteredStartCellIndices)-1:
			newdata.append('\n'+data[filteredEndCellIndices[i]:filteredStartCellIndices[i+1]]+'\n')
	# add stuff after last cell
	newdata.append(data[filteredEndCellIndices[-1]:])

	newdata = '\n'.join(newdata)

	return newdata

### NORMALIZATION 2 - REMOVE COMMENTS
def removeMathematicaComments(data):

	# find indices of start of Mathematica-comment
	exprStart = '\n(*'
	exprEnd = '*)'
	lenExprEnd = len(exprEnd)
	startCommentIndices = []
	found = data.find(exprStart)
	if found == -1:
		return data
	else:
		startCommentIndices = [found]
	count = data.count(exprStart)
	for i in xrange(0,count):
		start = data.find(exprStart,startCommentIndices[-1]+1)
		if start != -1:
			startCommentIndices.append(start)

	# find first closing bracket for each hit
	len_startCommentIndices = len(startCommentIndices)
	endCommentIndices = []
	for ind in startCommentIndices:
		endCommentIndices.append(data.find(exprEnd,ind))

	# construct data
	# add stuff before first comment
	newdata = [data[:startCommentIndices[0]]]
	for i in xrange(len(startCommentIndices)):
		# add stuff between comments
		if i<len(startCommentIndices)-1:
			newdata.append('\n'+data[endCommentIndices[i]+lenExprEnd:startCommentIndices[i+1]]+'\n')
	# add stuff after last cell
	newdata.append(data[endCommentIndices[-1]+lenExprEnd:])

	newdata = '\n'.join(newdata)

	return newdata


### NORMALIZATION 3 - REMOVE WHITESSPACES
def removeWhitespaces(data):

	# remove unnecessary spaces
	newdata = data.split(' ')

	newdata = [i for i in newdata if i != '']
	newdata = ' '.join(newdata)
	newdata = newdata.replace('\n ','\n')

	# remove unnecessary newlines
	newdata = newdata.split('\n')
	newdata = [i for i in newdata if i != '']

	# remove trailing whitespaces
	for i,line in enumerate(newdata):
		newdata[i] = line.strip()

	newdata = '\n'.join(newdata)

	return newdata


### NORMALIZATION 4 - REMOVE LINE CARRYS
def removeLineCarry(data):
	newdata = data.replace('\\\n','')
	newdata = newdata.replace('\ ','')
	return newdata


if __name__ == "__main__" and len(sys.argv) == 2:

	filename = sys.argv[1]
	ext = filename.split('.')[-1]

	if ext == 'nb':
		print "normalizing file: ",filename
		inp = open(filename,'r')
		data = inp.read()
		inp.close()

		data = removeNLinExpr(data,'Cell[BoxData[')
		data = removeMathematicaComments(data)
		data = removeWhitespaces(data)
		data = removeLineCarry(data)

		out = open(filename,'w')
		out.write(data)
		out.close()





# TODO
# alle Optionen ausser StyleDefinitions enternen
# (am Ende des Notebooks)
