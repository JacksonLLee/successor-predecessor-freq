# Modeling Brazilian Portuguese truncation by successor and predecessor frequencies
# Mike Pham, Jackson Lee, and Bruna Moreira
#
# citation:
# Pham, Mike, Jackson L. Lee, and Bruna da Costa Moreira. 2014.
# "Modeling Brazilian Portuguese truncation by successor and predecessor frequencies".
# Midwest Speech and Language Days 2014, University of Illinois at Urbana-Champaign. May 2-3, 2014.

import math
import string
import subprocess

def printTerminalTxt(s, f):
	'''
		prints s to terminal and text file
	'''
	print s
	f.write(s + '\n')

#######################################################################
###	reads in lexicon, input full forms, and outputs numbers			###
#######################################################################

lexicon = open('pt_br.txt').read().lower().split('\r\n')
# lexicon = open('Ncorpus.txt').read().lower().split('\n')
#testwords = open('input.txt').read().lower().split('\n')
testwords = [x[:x.index('\t')].replace('\n','').replace('|','') for x in open('goldStandard.txt')]
goldStandard = [x[:x.index('\t')].replace('\n','') for x in open('goldStandard.txt')]

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

###############################################################################
###	This builds up the full form incrementally from the first letter,		###
###	checking each time to see how many words in the lexicon can be formed	###
### from that truncated form												###
###############################################################################
for (fullform, gold) in zip(testwords, goldStandard):
	fullform = fullform.lower()
	fullformReversed = fullform[::-1]
	trunc = ''
	truncReversed = ''
	truncdisplay = 'trunc:' + '\t\t'
	perletterdisplay = 'suc-freq:' + '\t'
	logcountdisplay = 'log(SF):' + '\t'
#	perletterPFdisplay = 'pred-freq:' + '\t' # for predecessor freq
#	logcountPFdisplay = 'log(PF):' + '\t' # for predecessor freq
	perletterPFdisplay = '' # for predecessor freq
	logcountPFdisplay = '' # for predecessor freq
	truncrankdisplay = 'lex-freq:' + '\t'

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

	printTerminalTxt('----------' + '\n' + string.lower(fullform), output)
	outTex.write('%s\n\n%s\n\n\\vspace{1em}\n\n' % (fullform, gold.replace('|','$|$')))
	outTex.write('\\begin{tabular}{l|%s}\n\n' % ('l'*len(fullform)))
	goldPosition = gold.index('|')

	for (e, (letter, letterReversed)) in enumerate(zip(fullform, fullformReversed)):
		count = 0
		countReversed = 0
		truncrank = 1
		trunc = trunc + letter
		truncReversed = truncReversed + letterReversed

		truncdisplay = truncdisplay + letter + '\t'
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

		######################################
		##	Builds nicer display of numbers	##
		######################################
		perletterdisplay = perletterdisplay + str(count) + '\t'
		logcountdisplay = logcountdisplay + str(logcount) + '\t'
		perletterPFdisplay = '\t' + str(countReversed) + perletterPFdisplay
		logcountPFdisplay =  '\t' + str(logcountReversed) + logcountPFdisplay
		truncrankdisplay = truncrankdisplay + str(truncrank) + '\t'

		perletterdisplayTex = perletterdisplayTex + str(count) + ' & '
		logcountdisplayTex = logcountdisplayTex + str(logcount) + ' & '
		perletterPFdisplayTex = ' & ' + str(countReversed) + perletterPFdisplayTex
		logcountPFdisplayTex =  ' & ' + str(logcountReversed) + logcountPFdisplayTex
		truncrankdisplayTex = truncrankdisplayTex + str(truncrank) + ' & '

	printTerminalTxt(gold + '\n', output)
	printTerminalTxt(truncdisplay, output)
	printTerminalTxt(perletterdisplay, output)
	printTerminalTxt(logcountdisplay, output)
	printTerminalTxt('pred-freq:' + perletterPFdisplay, output)
	printTerminalTxt('log(PF):' + logcountPFdisplay, output)
	printTerminalTxt(truncrankdisplay, output)

	outTex.write(truncdisplayTex[:-3] + ' \\\\ \n')
	outTex.write(perletterdisplayTex[:-3] + ' \\\\ \n')
	outTex.write(logcountdisplayTex[:-3] + ' \\\\ \n')
	outTex.write('pred-freq:' + perletterPFdisplayTex + ' \\\\ \n')
	outTex.write('log(PF):' + logcountPFdisplayTex + ' \\\\ \n')
	outTex.write(truncrankdisplayTex[:-3] + ' \\\\ \n')

	outTex.write('\\end{tabular}\n\n')
	outTex.write('\\vspace{3em}\n\n')

# close open file objects and compile .tex file

outTex.write('\\end{document}\n')
outTex.close()
output.close()

subprocess.call(('latex', 'outlatex.tex'))
subprocess.call(('dvipdf', 'outlatex.dvi'))
