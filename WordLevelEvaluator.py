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


from TextGrid_Parsing import TextGrid2Dict, TextGrid2WordList
from Utilz import getMeanAndStDevError


ANNOTATION_EXT = '.TextGrid'
DETECTED_EXT = '.dtwDurationsAligned'

##################################################################################

# utility enumerate constants class 
class Enumerate(object):
  def __init__(self, names):
    for number, name in enumerate(names.split()):
      setattr(self, name, number)

tierAliases = Enumerate("phonemeLevel wordLevel phraseLevel")

'''
calculate evaluation metric
For now works only with begin ts
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
        detectedWordList= mlf2PhonemesAndTsList(detectedURI)
    elif whichLevel == tierAliases.wordLevel or whichLevel == tierAliases.phraseLevel :
        detectedWordList= mlf2WordAndTsList(detectedURI)
    return detectedWordList
        

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
    # prepare list of detected tokens. remove detected tokens NOISE, sil, sp entries from  detectedTokenList
    detectedTokenListNoPauses = []   #result 
    for detectedTsAndToken in detectedTokenList:
        if detectedTsAndToken[2] != 'sp' and detectedTsAndToken[2] != 'sil' and detectedTsAndToken[2] != 'NOISE':
            detectedTokenListNoPauses.append(detectedTsAndToken)

    ######################  
    # prepare list of phrases from ANNOTATION. remove empy annotaion tokens 
    
    annotationTokenListA = TextGrid2WordList(annotationURI, whichLevel)     
    
    annotationTokenListNoPauses = []
    for annoTsAndToken in annotationTokenListA:
        if annoTsAndToken[2] != "" and not(annoTsAndToken[2].isspace()): # skip empty phrases
                annotationTokenListNoPauses.append(annoTsAndToken)
    
    if len(annotationTokenListNoPauses) == 0:
        logging.warn(annotationURI + ' is empty!')
        return alignmentErrors
    
    
    if len(detectedTokenListNoPauses) == 0:
        logging.warn(' detected wotd list is empty!')
        return alignmentErrors
    
    # loop in tokens of annotation
    currentWordNumber = 0
    for annoTsAndToken in annotationTokenListNoPauses:
       
        annoTsAndToken[2] = annoTsAndToken[2].strip()
        subtokens = annoTsAndToken[2].split(" ")
        numWordsInPhrase = len(subtokens)
        
        if numWordsInPhrase == 0:
            sys.exit('token with no sutokens in annotation file!')
        
        if  currentWordNumber + 1 > len(detectedTokenListNoPauses):
            sys.exit('more tokens (words/phrases/phonemes) detected than in annotation. No evaluation possible')
            
        detectedTsAndToken = detectedTokenListNoPauses[currentWordNumber]
        
        # calc difference phrase begin Ts (0) and endTs (1)
        for i in (0,1):
            annotatedTs = annoTsAndToken[i]
            detectedTs = detectedTsAndToken[i]

            currAlignmentError = calcError(annotatedTs, detectedTs)
            alignmentErrors.append(currAlignmentError)
        
        
        
        #### UPDATE: proceed in detection the number of subtokens in current token          
        currentWordNumber +=numWordsInPhrase
                
    return  alignmentErrors
        

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
        tierNameWordAligned = 'wordAligned'
        tierNamePhonemeAligned =  'phonemeAligned'
        alignedResultPath, fileNameWordAnno = addAlignmentResultToTextGridFIle( detectedURI, annoURI,   tierNameWordAligned, tierNamePhonemeAligned)
        
        openTextGridInPraat(alignedResultPath, fileNameWordAnno, audio_URI + '.wav')
        
        return mean, stDev,  median, alignmentErrors
    
             
   

##################################################################################

if __name__ == '__main__':
    
    evalOneFile(sys.argv)
    
    
#     PATH_TEST_DATASET = '/Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/ISTANBUL/goekhan/'
#     PATH_TEST_DATASET = '/Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/ISTANBUL/safiye/'
#     
#     audioName = ''
#     annotationURI = os.path.join(PATH_TEST_DATASET,  audioName + ANNOTATION_EXT)
#     detectedURI = os.path.join(PATH_TEST_DATASET,  audioName +  DETECTED_EXT)
#      
# #     annotationURI = '/Volumes/IZOTOPE/sertan_sarki/segah--sarki--curcuna--olmaz_ilac--haci_arif_bey/21_Recep_Birgit_-_Olmaz_Ilac_Sine-i_Sad_Pareme/21_Recep_Birgit_-_Olmaz_Ilac_Sine-i_Sad_Pareme_meyan2_from_69_194485_to_79_909261.TextGrid'
# #     detectedURI = '~//Downloads/blah'
# #      
#     mean, stDev,  median, alignmentErrors  = evalOneFile(argv[1], argv[2], argv[3])
# #     mean, stDev,  median, alignmentErrors  = evalOneFile(annotationURI, detectedURI, tierAliases.wordLevel)
#     


    
    
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
    