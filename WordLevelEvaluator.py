# -*- coding: utf-8 -*-
'''
Created on Mar 5, 2014

This metric is strict, because an error might be counted twice if end and begin of consecutive tokens coincide. 
This happens when there is no silent pause between tokens both in annotation and detected result. 
This is similar to proposed by shriberg on sentence boundary detection.  
@author: joro
'''

import os
import sys
import numpy
from PraatVisualiser import mlf2PhonemesAndTsList, mlf2WordAndTsList,\
    addAlignmentResultToTextGridFIle, openTextGridInPraat
import logging


# this allows path to packages to be resolved correctly (on import) from outside of eclipse 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
sys.path.append(parentDir)

# utilsLyrics
pathUtils = os.path.join(parentDir,  'utilsLyrics')
sys.path.append(pathUtils )


from TextGrid_Parsing import TextGrid2Dict, TextGrid2WordList, tier_names
from Utilz import getMeanAndStDevError


ANNOTATION_EXT = '.TextGrid'
DETECTED_EXT = '.dtwDurationsAligned'
AUDIO_EXT = '.wav'

##################################################################################

# utility enumerate constants class 
class Enumerate(object):
  def __init__(self, names):
    for number, name in enumerate(names.split()):
      setattr(self, name, number)

tierAliases = Enumerate("phonemeLevel wordLevel phraseLevel")


def determineSuffix(withDuration, withSynthesis, evalLevel):
    '''
    lookup suffix for result files  depending on which algorithm used
    '''    
    evalLevelToken = tier_names[evalLevel]
    if withDuration:
        if withSynthesis:
            tokenAlignedSuffix =  '.' + evalLevelToken + 'DurationSynthAligned'
            phonemesAlignedSuffix = '.phonemesDurationSynthAligned'
        else:
            tokenAlignedSuffix = '.' + evalLevelToken + 'DurationAligned'
            phonemesAlignedSuffix = '.phonemesDurationAligned'
    else:
        tokenAlignedSuffix = '.' + evalLevelToken + 'Aligned'
        phonemesAlignedSuffix = '.phonemesAligned'
    return tokenAlignedSuffix, phonemesAlignedSuffix


'''
calculate evaluation metric
For now works only with begin ts
@deprecated
'''
def wordsList2avrgTxt(annotationWordList, detectedWordList):
    
    sumDifferences = 0;
    matchedWordCounter = 0;
    
    # parse annotation word ts and compare each with its detected
    for tupleWordAndTs in annotationWordList:
        for tupleDetectedWordAndTs in  detectedWordList:
            
            if tupleWordAndTs[1] == tupleDetectedWordAndTs[1]:
                currdifference = abs(float(tupleWordAndTs[0]) - float(tupleDetectedWordAndTs[0]))
                matchedWordCounter +=1
                sumDifferences = sumDifferences + currdifference
                # from beginning of list till first matched word
                break
    return sumDifferences/matchedWordCounter
            
            
            
    return

def evalAlignmentError(annotationURI, detectedURI, whichLevel=2 ):
    '''reads detected from htk mlf
    @param detectedURI: URI of htk-mlf format
    @param annotationURI: URI of Praat annotaiton textgrid. 
    @param whichLevel, 0- phonemeLevel, 1 -wordLevel,  2 - phraseLevel. The level at which to compare phrases 
    reads only the layer from with name correspondingly phonemes, words or phrases

    
    '''
    detectedWordList = loadDetectedTokenListFromMlf( detectedURI, whichLevel=2 )
    evalErrors = _evalAlignmentError(annotationURI, detectedWordList, whichLevel )
    return evalErrors


def loadDetectedTokenListFromMlf( detectedURI, whichLevel=2 ):

    ####################### 
    # # prepare list of phrases/phonemes from DETECTED:
    if whichLevel == tierAliases.phonemeLevel:
        detectedTokenList= mlf2PhonemesAndTsList(detectedURI)
    elif whichLevel == tierAliases.wordLevel or whichLevel == tierAliases.phraseLevel :
        detectedTokenList= mlf2WordAndTsList(detectedURI)
    else:
        sys.exit("level could be only phoneme- or word-level")
    return detectedTokenList
        








def _evalAlignmentError(annotationURI, detectedTokenList, whichLevel=2 ):
    '''
Calculate alignment errors. Does not check token identities, but proceeds successively one-by-one  
Make sure number of detected tokens (wihtout counting sp, sil ) is same as number of annotated tokens 

    @param detectedURI: a list of triples: (startTs, endTs, wordID) 
    @param annotationURI: URI of Praat annotaiton textgrid. 
    @param whichLevel, 0- phonemeLevel, 1 -wordLevel,  2 - phraseLevel. The level at which to compare phrases 
    reads only the layer from with name correspondingly phonemes, words or phrases
    
    token: could be phoneme (consists of one subtoken -phoneme itself), word (consists of one subtoken -word itself) or phrase (consist of subtokens words ) 

TODO: eval performance of end timest. only and compare with begin ts. 

    '''
    alignmentErrors = []
    
        ######################  
    annotationTokenListNoPauses, detectedTokenListNoPauses, dummy, dummy = stripNonLyricsTokens(annotationURI, detectedTokenList, whichLevel)
    
    if len(annotationTokenListNoPauses) == 0:
        logging.warn(annotationURI + ' is empty!')
        return alignmentErrors
    
    
    if len(detectedTokenListNoPauses) == 0:
        logging.warn(' detected token list is empty!')
        return alignmentErrors
    
    # loop in tokens of gr truth annotation
    currentWordNumber = 0
    for currAnnoTsAndToken in annotationTokenListNoPauses:
       
        currAnnoTsAndToken[2] = currAnnoTsAndToken[2].strip()
        subtokens = currAnnoTsAndToken[2].split()
        numWordsInPhrase = len(subtokens)
        
        if numWordsInPhrase == 0:
            sys.exit('token (phrase) with no subtokens (words) in annotation file!')
        
        if  currentWordNumber >= len(detectedTokenListNoPauses):
            sys.exit(' number of tokens in annotation {} differs from  num tokens detected {}. No evaluation possible'.format( currentWordNumber, len(detectedTokenListNoPauses)))
            
        
        beginAlignmentError, endAlignmentError = calcErrorBeginAndEndTs(detectedTokenListNoPauses, currAnnoTsAndToken, currentWordNumber, numWordsInPhrase)        
        
        alignmentErrors.append(beginAlignmentError)
        alignmentErrors.append(endAlignmentError)
        
        #### UPDATE: proceed in detection the number of subtokens in current token          
        currentWordNumber +=numWordsInPhrase
    
    # sanity check: 
    if currentWordNumber != len(detectedTokenListNoPauses):
            sys.exit(' number of tokens in annotation {} differs from  num tokens detected {}. No evaluation possible'.format( currentWordNumber, len(detectedTokenListNoPauses)))

                
    return  alignmentErrors



'''
prepare list of tokens. remove detected tokens NOISE, sil, sp entries from  detectedTokenList and annoTokenList

'''
def stripNonLyricsTokens(annotationURI, detectedTokenList, whichLevel):
    detectedTokenListNoPauses = [] #result
    for detectedTsAndToken in detectedTokenList:
        if detectedTsAndToken[2] != 'sp' and detectedTsAndToken[2] != 'sil' and detectedTsAndToken[2] != 'NOISE' and detectedTsAndToken[2] != '_SAZ_':
            detectedTokenListNoPauses.append(detectedTsAndToken)
    
######################
# prepare list of phrases from ANNOTATION. remove empy annotaion tokens
    try:
        annotationTokenListA = TextGrid2WordList(annotationURI, whichLevel)
    except Exception as errorMsg:
        sys.exit(str(errorMsg))
    
    
    
    annotationTokenListNoPauses = []
    
    for currAnnoTsAndToken in annotationTokenListA:
        if currAnnoTsAndToken[2] != "" and not (currAnnoTsAndToken[2].isspace()): # skip empty phrases
            annotationTokenListNoPauses.append(currAnnoTsAndToken)
    
    return annotationTokenListNoPauses, detectedTokenListNoPauses, float(annotationTokenListA[-1][1]), detectedTokenList[-1][1]



def calcErrorBeginAndEndTs(detectedTokenListNoPauses, annoTsAndToken, currentWordNumber, numWordsInPhrase):
    '''
    @param annoTsAndToken: - might have 1 or more tokens 
    @param detectedTokenListNoPauses:  list of tokens. here reference only the relevant beginning and ending tokens
    '''
    # calc difference phrase begin Ts
    annotatedTs = annoTsAndToken[0]
    detectedTs = detectedTokenListNoPauses[currentWordNumber][0]
    beginAlignmentError = calcError(annotatedTs, detectedTs)
    
    # calc difference phrase endTs (1)
    annotatedTs = annoTsAndToken[1]
    detectedTs = detectedTokenListNoPauses[currentWordNumber + numWordsInPhrase - 1][1]
    endAlignmentError = calcError(annotatedTs, detectedTs)
    
    return beginAlignmentError, endAlignmentError

        

def calcError(annotatedTokenTs, detectedTokenTs):
    '''
    abs error btw a token form anno and detected 
    '''
    currAlignmentError = float(annotatedTokenTs) - float(detectedTokenTs)
    currAlignmentError = numpy.round(currAlignmentError, decimals=2)
    return currAlignmentError      
    


def evalOneFile(argv):
        ''' Main utility function
        ''' 
       
        if len(argv) != 5:
            print ("usage: {} <URI_annotation> <URI_detected> <evalLevel> <URI_audio>".format(argv[0]) )
            sys.exit();
             
        annoURI = argv[1]
        detectedURI = argv[2]
        evalLevel = int(argv[3])
        audio_URI = argv[4]
        alignmentErrors  = evalAlignmentError(annoURI , detectedURI  , evalLevel)
        
        mean, stDev, median = getMeanAndStDevError(alignmentErrors)
        
        # optional
#         print "mean : ", mean, "st dev: " , stDev
        print  mean, " ", stDev
        
        
         ### OPTIONAL : open detection and annotation in praat. can be provided on request
#         wordAlignedSuffix = '"wordsAligned"'
#         phonemeAlignedSuffix =  '"phonemesAligned"'
#         alignedResultPath, fileNameWordAnno = addAlignmentResultToTextGridFIle( detectedURI, annoURI,   wordAlignedSuffix, phonemeAlignedSuffix)
#         
#          
#         openTextGridInPraat(alignedResultPath, fileNameWordAnno, audio_URI)
        
        return mean, stDev,  median, alignmentErrors
    
             
   

##################################################################################

if __name__ == '__main__':
###########    test eval  with lists
    # TODO: do a unit test here and put in example folder
#     #    
#        
########### test eval with files
 
#     evalOneFile(sys.argv)
    
    ########## 1 example with detected mlf file: 
#     PATH_TEST_DATASET = 'example/'
#       
#     audioName = '01_Bakmiyor_3_nakarat'
#     annotationURI = os.path.join(PATH_TEST_DATASET,  audioName + ANNOTATION_EXT)
#     detectedURI = os.path.join(PATH_TEST_DATASET,  audioName +  DETECTED_EXT)
#     audioURI = os.path.join(PATH_TEST_DATASET,  audioName + AUDIO_EXT)
#   
#  
#     mean, stDev,  median, alignmentErrors  = evalOneFile([__file__, annotationURI, detectedURI, tierAliases.wordLevel, audioURI ])
#      
    ############### 2  example with detected tsv file
#     PATH_TEST_DATASET = 'example/'
#       
#     audioName = '05_Semahat_Ozdenses_-_Bir_Ihtimal_Daha_Var_0_zemin_from_69_5205_to_84_2'
#     annotationURI = os.path.join(PATH_TEST_DATASET,  audioName + ANNOTATION_EXT)
#     
#     # TODO: load from file
# #     detectedURI = os.path.join(PATH_TEST_DATASET,  audioName +  '.phrasesDurationAligned')
#   
#     detectedList =   [[0.61, 0.94, u'Bir'], [1.02, 3.41, u'ihtimal'], [3.42, 4.11, u'daha'], [4.12, 5.4, u'var'], [5.5, 7.93, '_SAZ_'], \
#     [8.03, 8.42, u'o'], [8.46, 8.83, u'da'], [8.86, 10.65, u'\xf6lmek'], [10.66, 11.04, u'mi'], [11.05, 14.39, u'dersin']]
#     
#        
#     alignmentErrors = _evalAlignmentError(annotationURI, detectedList, tierAliases.phraseLevel)
#     mean, stDev, median = getMeanAndStDevError(alignmentErrors)
#         
#     print  mean, " ", stDev
    
 ############### 3  other example with detected tsv file
    PATH_TEST_DATASET = 'example/'
      
    audioName = '01_Bakmiyor_0_zemin'
    annotationURI = os.path.join(PATH_TEST_DATASET,  audioName + ANNOTATION_EXT)
    
    # TODO: load from file
#     detectedURI = os.path.join(PATH_TEST_DATASET,  audioName +  '.phrasesDurationAligned')
  
        

    detectedList =    [ [0.386834650351, 0.996834650351,    '_SAZ_'],
                     [0.996834650351,3.17683465035,    u'Bakmıyor'],
                      [3.17683465035,4.44683465035,  u'çeşmi'],
                      [4.44683465035,6.02683465035,    'siyah'],
                      [6.02683465035,11.5068346504,    u'feryâde']]
    
    alignmentErrors = _evalAlignmentError(annotationURI, detectedList, tierAliases.phraseLevel)
    mean, stDev, median = getMeanAndStDevError(alignmentErrors)
        
    print  mean, " ", stDev
    
    ############# FROM HERE ON: old testing code for word-level eval 
#     tmpMLF= '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik/1-05_Ruzgar_Soyluyor_Simdi_O_Yerlerde/1-05_Ruzgar_Soyluyor_Simdi_O_Yerlerde_nakarat2_from_192.962376_to_225.170507.phone-level.output'
#     listWordsAndTs = mlf2WordAndTsList(tmpMLF)
#   
#     
#     
#   
# # TODO: error in parsing of sertan's textGrid
#     textGridFile = '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik/1-05_Ruzgar_Soyluyor_Simdi_O_Yerlerde/1-05_Ruzgar_Soyluyor_Simdi_O_Yerlerde.TextGrid'
# #     textGridFile='/Volumes/IZOTOPE/adaptation_data/kani_karaca-cargah_tevsih.TextGrid'
# #     textGridFile = '/Users/joro/Documents/Phd/UPF/Example_words_phonemes.TextGrid'
#     textGridFile = '/Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/04_Hamiyet_Yuceses_-_Bakmiyor_Cesm-i_Siyah_Feryade/04_Hamiyet_Yuceses_-_Bakmiyor_Cesm-i_Siyah_Feryade_gazel.wordAnnotation.TextGrid'
#     
#     
#     
#     
#     listWordsAndTsAnnot = TextGrid2WordList(textGridFile)
#     
#     
#     annotationWordList = [[0.01, 'sil'], [0.05, 'rUzgar'], [0.9,'Simdi']]
#     avrgDiff = wordsList2avrgTxt(annotationWordList,listWordsAndTs)
#     
#     
#     print avrgDiff
    