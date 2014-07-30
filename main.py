# Modeling Brazilian Portuguese truncation using successor frequencies
# Mike Pham, Jackson Lee, and Bruna Moreira

import math
import string
import subprocess
import codecs

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

def intersectionBefore(points1, points2):
	for (idx, (p1, p2)) in enumerate(zip(points1, points2)):
		if p2 > p1:
			return idx

def intersectionClosest(points1, points2):
#   points1[idx1] *   * points1[idx2]
#				  \ /
#				   *  <--- intersection point
#				  / \
#   points2[idx1] *   * points2[idx2]
	for (idx, (p1, p2)) in enumerate(zip(points1, points2)):
		if p2 > p1:
			idx1 = idx - 1
			idx2 = idx

			diff1 = abs(points1[idx1] - points2[idx1])
			diff2 = abs(points1[idx2] - points2[idx2])

			if diff1 <= diff2:
				return idx
			else:
				return idx+1


#######################################################################
###	reads in lexicon, input full forms, and outputs numbers			###
#######################################################################

lexicon = open('pt_br.txt').read().lower().split('\r\n')
# lexicon = open('Ncorpus.txt').read().lower().split('\n')

#goldStandardFilename = 'goldStandard.txt'
#goldStandardFilename = 'goldStandard_MP.txt' # expanded gold standard list
goldStandardFilename = 'goldStandard_MP_bin.txt' # expanded gold standard list, with binary feet marked

testwords = [x[:x.index('\t')].replace('\n','').replace('|','').replace('$','') for x in open(goldStandardFilename) if (not x.startswith('#'))]
goldStandard = [x[:x.index('\t')].replace('\n','').replace('$','') for x in open(goldStandardFilename) if not x.startswith('#')]
goldStandardBinFoot = [x[:x.index('\t')].replace('\n','').replace('|','') for x in open(goldStandardFilename) if not x.startswith('#')]

output = open('output.csv', 'w')

Rscriptname = 'Rplots/generate_plots.R'
Rscript = open(Rscriptname, 'w')

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
SFPFpredictBeforeList = list()
SFPFpredictClosestList = list()
truncPointList = list()
truncPointBinFootList = list()


###############################################################################
###	This builds up the full form incrementally from the first letter,		###
###	checking each time to see how many words in the lexicon can be formed	###
### from that truncated form												###
###############################################################################
for (fullform, gold, goldBinFoot) in zip(testwords, goldStandard, goldStandardBinFoot):
	print fullform
	truncPoint = gold.index('|')
	truncPointBinFoot = goldBinFoot.index('$')
	truncPointList.append(truncPoint)
	truncPointBinFootList.append(truncPointBinFoot)
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
	outTex.write('{0}\n\n{1}\n\n\\vspace{{1em}}\n\n'.format(fullform, gold.replace('|','$|$')))
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
	PFpredict = elbowPoint(logcountReversedList[::-1])
	SFPFpredictBefore = intersectionBefore(logcountList, logcountReversedList[::-1])
	SFPFpredictClosest = intersectionClosest(logcountList, logcountReversedList[::-1])

	SFpredictList.append(SFpredict)
	PFpredictList.append(PFpredict)
	SFPFpredictBeforeList.append(SFPFpredictBefore)
	SFPFpredictClosestList.append(SFPFpredictClosest)

	outTex.write('SF point: ' + str(SFpredict)+'\n\n')
	outTex.write('PF point: ' + str(PFpredict)+'\n\n')

	outTex.write('SF+PF-before point: ' + str(SFPFpredictBefore) + '\n\n')
	outTex.write('SF+PF-closest point: ' + str(SFPFpredictClosest) + '\n\n')

	outTex.write('\\vspace{3em}\n\n')

	## write R script ##
	Rscript.write('postscript(\'Rplots/%s.eps\')\n' % (fullform))
	Rscript.write('sf <- c(%s)\n' % (','.join([str(x) for x in logcountList])))
	Rscript.write('pf <- c(%s)\n' % (','.join([str(x) for x in logcountReversedList[::-1]])))
	Rscript.write('y_range <- range(sf,pf)\n')

	Rscript.write('plot(sf, type="o", pch=21, lty=1, ylim=y_range, axes=FALSE, ann=FALSE)\n')
	Rscript.write('lines(pf, type="o", pch=22, lty=2)\n')

	x_axis_label = ''
	for i in range(len(fullform)):
		if i < truncPoint:
			x_axis_label = x_axis_label + fullform[i].upper()
		else:
			x_axis_label = x_axis_label + fullform[i]

	Rscript.write('axis(1, at=1:%d, lab=c(%s))\n' % (len(fullform), ','.join(['"'+x+'"' for x in x_axis_label])))
	Rscript.write('axis(2, las=1)\n')

	Rscript.write('box()\n')

	Rscript.write('title(main="%s")\n' % (gold.replace('|','')))
	Rscript.write('title(ylab="log(freq)")\n')

	Rscript.write('legend(2, y_range[2], c("suc freq (SF)","pred freq (PF)"), pch=21:22, lty=1:2)\n')
	Rscript.write('dev.off()\n\n')




##########################################################
### evaluation
##########################################################

print

evaluationList = list()

SFevaluationList = list()
PFevaluationList = list()
SFPFevaluationList = list()
SFPF_closest_evaluationList = list()
BinFootevaluationList = list()

output.write('{0},{1},{2},{3},{4},{5},{6}\n'.format('word','truc-pt',
														'SF',
														'PF',
														'SFPF-before', 'SFPF-closest', 'BinaryFoot'))

for (gold, T, SF, PF, SFPF, SFPF_closest, binfoot) in zip(goldStandard, truncPointList, SFpredictList, PFpredictList, SFPFpredictBeforeList, SFPFpredictClosestList, truncPointBinFootList):
	SFeval = T-SF
	PFeval = T-PF
	SFPFeval = T-SFPF
	SFPFeval_closest = T - SFPF_closest
	BinFootEval = T - binfoot

	SFevaluationList.append(SFeval)
	PFevaluationList.append(PFeval)
	SFPFevaluationList.append(SFPFeval)
	SFPF_closest_evaluationList.append(SFPFeval_closest)
	BinFootevaluationList.append(BinFootEval)

	output.write('{0},{1},{2},{3},{4},{5},{6}\n'.format(gold, T,
														SFeval, 
														PFeval, 
														SFPFeval, SFPFeval_closest, BinFootEval))

lenGold = len(goldStandard)

output.write(',sum ->,{0},{1},{2},{3},{4}\n'.format(sum(SFevaluationList), 
													sum(PFevaluationList),
													sum(SFPFevaluationList), sum(SFPF_closest_evaluationList), sum(BinFootevaluationList)))

def sum_abs(L, plus=0):
	return sum([abs(x+plus) for x in L])

output.write(',abs. values ->,{0},{1},{2},{3},{4}\n'.format(sum_abs(SFevaluationList), 
															sum_abs(PFevaluationList), 
															sum_abs(SFPFevaluationList), sum_abs(SFPF_closest_evaluationList), sum_abs(BinFootevaluationList)))


############################################################
# close open file objects and compile .tex file

outTex.write('\\end{document}\n')
outTex.close()
output.close()
Rscript.close()

subprocess.call(('latex', 'outlatex.tex'))
subprocess.call(('dvipdf', 'outlatex.dvi'))
subprocess.call(('Rscript', Rscriptname))
