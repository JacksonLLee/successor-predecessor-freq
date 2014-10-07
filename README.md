successor-predecessor-freq
==========================

Modeling Brazilian Portuguese truncation (joint work with Mike Pham and Bruna Moreira)

- main.py: the major working script which takes input files (provided here), and outputs outlatex.tex (sample provided here) with the compiled .pdf as well
- goldStandard.txt: a list of Brazilian Portuguese nouns with their truncation point indicated; also act as test cases
- pt_br.txt: a Brazilian Portuguese lexicon (size = 350,000), with word token frequencies; obtained from online based on TV and/or movie subtitles, exact sources unclear.
(This file is available here: http://jacksonllee.com/private/data/pt_br.txt , 4.4 MB)
- outlatex.tex: output LaTeX file from main.py given goldStandard.txt and pt_br.txt

