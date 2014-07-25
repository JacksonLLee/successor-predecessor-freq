# Modeling Brazilian Portuguese truncation using successor frequencies
# Mike Pham, Jackson Lee, and Bruna Moreira

import math
import string
import subprocess

def printTerminalTxt(s, f):
	'''
		prints s to terminal and text file
	'''
	print s
	f.write(s + '\n')

def elbowPoint(points):
	'''takes a list of points and outputs the index of the list for maximal curvature'''
	secondDerivativeList = [points[i+1] + points[i-1] - 2*points[i] for i in range(1, len(points) - 1)]
	secondDerivativeListPointTuplesSorted = sorted(enumerate(secondDerivativeList), key=lambda x:x[1], reverse=True)
	return secondDerivativeListPointTuplesSorted[0][0] + 2

def intersection(points1, points2):
	for (idx, (p1, p2)) in enumerate(zip(points1, points2)):
		if p2 > p1:
			return idx+1


#######################################################################
###	reads in lexicon, input full forms, and outputs numbers			###
#######################################################################

lexicon = open('pt_br.txt').read().lower().split('\r\n')
# lexicon = open('Ncorpus.txt').read().lower().split('\n')
#testwords = open('input.txt').read().lower().split('\n')
#testwords = [x[:x.index('\t')].replace('\n','').replace('|','') for x in open('goldStandard.txt')]
#goldStandard = [x[:x.index('\t')].replace('\n','') for x in open('goldStandard.txt')]

#expanded gold standard list
testwords = [x[:x.index('\t')].replace('\n','').replace('|','') for x in open('goldStandard_MP.txt')]
goldStandard = [x[:x.index('\t')].replace('\n','') for x in open('goldStandard_MP.txt')]

output = open('output.txt', 'w')

lexDict = { x.split()[0].lower():int(x.split()[1]) for x in lexicon }
lexKeys = lexDict.keys()
#lexReversedKeys = list([x[::-1] for x in lexKeys])

#######################################################################
###	initialize LaTeX .tex file	###
#######################################################################

outTex = open('outlatex.tex', 'w')

outTex.write('\\documentclass{article}\n')
outTex.write('\\usepackage{booktabs}\n')
outTex.write('\\usepackage{color}\n')
outTex.write('\\usepackage[letterpaper, margin=.5in]{geometry}\n')
outTex.write('\\setlength{\\parindent}{0em}\n')
outTex.write('\\begin{document}\n')


SFpredictList = list()
PFpredictList = list()
SFPFpredictList = list()
truncPointList = list()


###############################################################################
###	This builds up the full form incrementally from the first letter,		###
###	checking each time to see how many words in the lexicon can be formed	###
### from that truncated form												###
###############################################################################
for (fullform, gold) in zip(testwords, goldStandard):
	print fullform
	truncPoint = gold.index('|')
	truncPointList.append(truncPoint)
	fullform = fullform.lower()
	fullformReversed = fullform[::-1]
	trunc = ''
	truncReversed = ''

#	truncdisplay = 'trunc:' + '\t\t'
#	perletterdisplay = 'suc-freq:' + '\t'
#	logcountdisplay = 'log(SF):' + '\t'
##	perletterPFdisplay = 'pred-freq:' + '\t' # for predecessor freq
##	logcountPFdisplay = 'log(PF):' + '\t' # for predecessor freq
#	perletterPFdisplay = '' # for predecessor freq
#	logcountPFdisplay = '' # for predecessor freq
#	truncrankdisplay = 'lex-freq:' + '\t'

	truncdisplayTex = 'trunc:' + ' & '
	perletterdisplayTex = 'suc-freq:' + ' & '
	logcountdisplayTex = 'log(SF):' + ' & '
#	perletterPFdisplayTex = 'pred-freq:' + ' & '
#	logcountPFdisplayTex = 'log(PF):' + ' & '
	perletterPFdisplayTex = ''
	logcountPFdisplayTex = ''
	truncrankdisplayTex = 'lex-freq:' + ' & '

	
	######################################################################
	##	This gets the frequency ranking of the full form in the corpus	##
	######################################################################
	try:
		fullrank = lexDict[fullform]
	except KeyError:
		continue

#	printTerminalTxt('----------' + '\n' + string.lower(fullform), output)
	outTex.write('%s\n\n%s\n\n\\vspace{1em}\n\n' % (fullform, gold.replace('|','$|$')))
	outTex.write('\\begin{tabular}{l|%s}\n\n' % ('l'*len(fullform)))
	goldPosition = gold.index('|')

	logcountList = list()
	logcountReversedList = list()

	for (e, (letter, letterReversed)) in enumerate(zip(fullform, fullformReversed)):
		count = 0
		countReversed = 0
		truncrank = 1
		trunc = trunc + letter
		truncReversed = truncReversed + letterReversed

#		truncdisplay = truncdisplay + letter + '\t'
		if e < goldPosition:
			letterTex = '{\\color{red}\\bf ' + letter + '}'
		else:
			letterTex = letter
		truncdisplayTex = truncdisplayTex + letterTex + ' & '

		
		for word in lexKeys:
			wordReversed = word[::-1]

			######################################################################
			##	This counts the number of possible restitutions from trunc form	##
			######################################################################
			if word.startswith(trunc):
				count += 1
				
				################################################################
				##	This figures out what the frequency rank of the full form ##
				##	is relative to all possible restitutions from the trunc	  ##
				################################################################

				wordrank = lexDict[word]
				if wordrank > fullrank:
					truncrank = truncrank + 1

			if wordReversed.startswith(truncReversed):
				countReversed += 1

		##################################################################
		##	This gets the log10 of the number of possible restitutions	##
		##################################################################		
		if count > 0:
			logcount = round(math.log(count,10), 5)
		else:
			logcount = 0
		
		if countReversed > 0:
			logcountReversed = round(math.log(countReversed,10), 5)
		else:
			logcountReversed = 0

		logcountList.append(logcount)
		logcountReversedList.append(logcountReversed)

		######################################
		##	Builds nicer display of numbers	##
		######################################
#		perletterdisplay = perletterdisplay + str(count) + '\t'
#		logcountdisplay = logcountdisplay + str(logcount) + '\t'
#		perletterPFdisplay = '\t' + str(countReversed) + perletterPFdisplay
#		logcountPFdisplay =  '\t' + str(logcountReversed) + logcountPFdisplay
#		truncrankdisplay = truncrankdisplay + str(truncrank) + '\t'

		perletterdisplayTex = perletterdisplayTex + str(count) + ' & '
		logcountdisplayTex = logcountdisplayTex + str(logcount) + ' & '
		perletterPFdisplayTex = ' & ' + str(countReversed) + perletterPFdisplayTex
		logcountPFdisplayTex =  ' & ' + str(logcountReversed) + logcountPFdisplayTex
		truncrankdisplayTex = truncrankdisplayTex + str(truncrank) + ' & '

#	printTerminalTxt(gold + '\n', output)
#	printTerminalTxt(truncdisplay, output)
#	printTerminalTxt(perletterdisplay, output)
#	printTerminalTxt(logcountdisplay, output)
#	printTerminalTxt('pred-freq:' + perletterPFdisplay, output)
#	printTerminalTxt('log(PF):' + logcountPFdisplay, output)
#	printTerminalTxt(truncrankdisplay, output)

	outTex.write(truncdisplayTex[:-3] + ' \\\\ \n')
	outTex.write(perletterdisplayTex[:-3] + ' \\\\ \n')
	outTex.write(logcountdisplayTex[:-3] + ' \\\\ \n')
	outTex.write('pred-freq:' + perletterPFdisplayTex + ' \\\\ \n')
	outTex.write('log(PF):' + logcountPFdisplayTex + ' \\\\ \n')
	outTex.write(truncrankdisplayTex[:-3] + ' \\\\ \n')

	outTex.write('\\end{tabular}\n\n')

	outTex.write('trunc point: ' + str(truncPoint) + '\n\n')

	SFpredict = elbowPoint(logcountList)
	PFpredict = elbowPoint(logcountReversedList)
	SFPFpredict = intersection(logcountList, logcountReversedList[::-1])

	SFpredictList.append(SFpredict)
	PFpredictList.append(PFpredict)
	SFPFpredictList.append(SFPFpredict)

	outTex.write('SF point: ' + str(SFpredict)+'\n\n')
	outTex.write('PF point: ' + str(PFpredict)+'\n\n')

	outTex.write('SF+PF point: ' + str(SFPFpredict) + '\n\n')

	outTex.write('\\vspace{3em}\n\n')

#	print logcountList
#	print logcountReversedList
#	print

##########################################################
### evaluation
##########################################################

print

evaluationList = list()

SFevaluationList = list()
PFevaluationList = list()
SFPFevaluationList = list()

printTerminalTxt('{0:15s} {1:10s} {2:10s} {3:10s} {4:10s} {5:12s} {6:12s}'.format('word',
																				'SF-after', 'SF-before',
																				'PF-after', 'PF-before',
																				'SFPF-after', 'SFPF-before'), output)

for (gold, T, SF, PF, SFPF) in zip(goldStandard, truncPointList, SFpredictList, PFpredictList, SFPFpredictList):
	SFeval = T-SF
	PFeval = T-PF
	SFPFeval = T-SFPF

	SFevaluationList.append(SFeval)
	PFevaluationList.append(PFeval)
	SFPFevaluationList.append(SFPFeval)

	printTerminalTxt('{0:15s} {1:10d} {2:10d} {3:10d} {4:10d} {5:12d} {6:12d}'.format(gold,
																				SFeval, SFeval+1,
																				PFeval, PFeval+1,
																				SFPFeval, SFPFeval+1), output)

lenGold = len(goldStandard)

printTerminalTxt('evaluation:', output)
printTerminalTxt('SF-after SF-before PF-after PF-before SFPF-after SFPF-before\n{0} {1} {2} {3} {4} {5}'.format(sum(SFevaluationList), sum(SFevaluationList)+lenGold, 
																			sum(PFevaluationList), sum(PFevaluationList)+lenGold,
																			sum(SFPFevaluationList), sum(SFPFevaluationList)+lenGold), output)



############################################################
# close open file objects and compile .tex file

outTex.write('\\end{document}\n')
outTex.close()
output.close()

subprocess.call(('latex', 'outlatex.tex'))
subprocess.call(('dvipdf', 'outlatex.dvi'))
