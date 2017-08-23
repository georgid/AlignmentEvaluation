
Copyright  2017  Music Technology Group - Universitat Pompeu Fabra

AlignmentEvaluation
==============================

A tool for computing common alignment metrics of tokens (a token could be at different granularity level: a phoneme, word or phrase - a group of words ). Done to evaluate results of a system for lyrics-to-audio alignment on different token levels. 
Three common metrics are implemented: 
1) mean average alignment error
2) accuracy 
3) accuracy with tolerance 
For definition of the metrics see Chapter 2.2.1 from [this thesis](http://compmusic.upf.edu/phd-thesis-georgi)

The algorithm considers only begin timestamps of each token. It is token-identities-agnostic, e.g. it does not try to match token-IDs between detected result and annotation, but proceeds successively one-by-one.  
Extendable to the evaluation for any token-based alignment (e.g. if a token is a phrase, note, section )


Supported detected file formats :  
- mlf format of [htk](htk.eng.cam.ac.uk/) 
- lab format  of tuples begin_timestamp, (end_timestamp), tokenID. End timestamp is optional, not considered.

Supported annotation file formats: 
- TextGrid of [Praat](www.praat.org/) 
- lab format (see above). When exported from many tools among which e.g. [Audacity](http://www.audacityteam.org/home/). When end time stamps are provided (begin_timestamp, end_timestamp, tokenID), they are ingored.

 


Enjoy!
 

BUILD INSTRUCTIONS:
------------------------------------------
- install [mir_eval](https://github.com/craffel/mir_eval)
- git clone https://github.com/georgid/AlignmentEvaluation
- cd <path_to_installed AlignmentEvaluation>
- python setup.py install




USAGE: 
---------------------------------------- 

### For .lab file 

[test.EvalMetricsTest.evalError_lab_test()](https://github.com/georgid/AlignmentEvaluation/blob/master/test/EvalMetricsTest.py#L56)

[test.EvalMetricsTest.evalAccuracy_lab_test()](https://github.com/georgid/AlignmentEvaluation/blob/master/test/EvalMetricsTest.py#L39)




### For .TextGrid file 

test.EvalMetricsTest.evalAccuracy_TextGird_test()

test.EvalMetricsTest.eval_error_textGrid_test()


There is also a module to convert automatically the decoded result to Praat's TextGrid format.
This enables the  visualization of the decoding result together with the groundTruth in Praat:
see PraatVisualiser.openTextGridInPraatopenTextGridInPraat() : opens the text Grid in Praat
NOTE: # deprecated due to error on opening word-level files... use instead tab2TextGrid 

As well make sure to change the path to your installed Praat program:
PraatVisualiser.PATH_TO_PRAAT

To change extensions edit variables in WordLevelEvaluator 
ANNOTATION_EXT = '.TextGrid'
DETECTED_EXT = '.dtwDurationAligned'
when parsing TextGrid: tier_names are expected as defined in TextGrid_Parsing




EXAMPLE: 
---------------------------------------- 
if decoded result is:
 
startTs endTs phonemeOrWord

0.0		1.11	sil

1.11	2.41	usagi

2.41	2.90	usagi

2.90	3.38	sp

3.38	4.15	nani

and annotation  is:

1.12 	usagi usagi 

3.56 	nani

...then the two detected phrases are considered to evaluate:  

1.11 2.90 usagi usagi 

and 

3.38 4.15	nani





LICENSE:
-------------------
AlignmentEvaluation is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation (FSF), either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see http://www.gnu.org/licenses/

CITATION: 
----------------------
please cite 
Dzhambazov, G.,  - Knowledge-based Probabilistic Modeling for Tracking Lyrics in Music Audio Signals, PhD Thesis


