'''
Created on Feb 24, 2015

@author: joro
'''
from WordLevelEvaluator import stripNonLyricsTokens,\
    loadDetectedTokenListFromMlf
import logging
import sys
import os

# file parsing tools as external lib 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 

pathUtils = os.path.join(parentDir, 'utilsLyrics')
sys.path.append(pathUtils )
from utilsLyrics.Utilz import  readListOfListTextFile

def evalAccuracy(URIrecordingAnno, outputHTKPhoneAlignedURI, whichTier, startIdx, endIdx ):
    
    detectedTokenList = loadDetectedTokenListFromMlf( outputHTKPhoneAlignedURI, whichTier )
    durationCorrect, totalDuration = _evalAccuracy(URIrecordingAnno, detectedTokenList, whichTier, startIdx, endIdx)
    return  durationCorrect, totalDuration 

def _evalAccuracy(annotationURI, detectedTokenList, whichTier, startIdx, endIdx):
    '''
Calculate accuracy as suggested in
Fujihara: LyricSynchronizer: Automatic Synchronization System Between Musical Audio Signals and Lyrics
Does not check token identities, but proceeds successively one-by-one  
Make sure number of detected tokens (wihtout counting sp, sil ) is same as number of annotated tokens 

    @param detectedTokenList: a list of triples: (startTs, endTs, wordID) 
    @param annotationURI: URI of Praat annotaiton textgrid. 
    @param whichTier works only with the tier from TextGrid_Parsing  tier_names = ["phonemes", 'words', "phrases", "lyrics-syllables-pinyin", 'sections'];
    @param startIdx index of boundary in tier to be considered as start one  (from TextGrid -1 )
    @param endIdx index of end token
    
    token: could be phoneme (consists of one subtoken -phoneme itself), word (consists of one subtoken -word itself) or phrase (consist of subtokens words ) 

TODO: eval performance of end timest. only and compare with begin ts. 

    '''
    
        ######################  
    annotationTokenListNoPauses, detectedTokenListNoPauses, finalTsAnno, finalTsDetected, initialTimeOffset = stripNonLyricsTokens(annotationURI, detectedTokenList, whichTier, startIdx, endIdx)
    
    # WoRKAROUND. because currenty I dont store final sil in detected textFile .*Aligned 
#     finalTsDetected = finalTsAnno

    durationCorrect = 0;

    if len(annotationTokenListNoPauses) == 0:
        logging.warn(annotationURI + ' is empty! Check code')
        return durationCorrect
    
    
    if len(detectedTokenListNoPauses) == 0:
        logging.warn(' detected token list is empty! Check code')
        return durationCorrect
    
    # loop in tokens of gr truth annotation
    durationCorrect = min(float(annotationTokenListNoPauses[0][0]), detectedTokenListNoPauses[0][0]) - initialTimeOffset
    
    currentWordNumber = 0
    for idx, currAnnoTsAndToken in enumerate(annotationTokenListNoPauses):
       
        currAnnoTsAndToken[2] = currAnnoTsAndToken[2].strip()
        subtokens = currAnnoTsAndToken[2].split()
        numWordsInPhrase = len(subtokens)
        
        if numWordsInPhrase == 0:
            sys.exit('token (phrase) with no subtokens (words) in annotation file!')
        
        if  currentWordNumber >= len(detectedTokenListNoPauses):
            sys.exit(' number of tokens in annotation {} differs from  num tokens detected {}. No evaluation possible'.format( len(annotationTokenListNoPauses), len(detectedTokenListNoPauses)))
            
        
        durationCorrect += calcCorrect(detectedTokenListNoPauses, annotationTokenListNoPauses, idx, currentWordNumber, numWordsInPhrase,  finalTsAnno, finalTsDetected)        
        
        
        #### UPDATE: proceed in detection the number of subtokens in current token          
        currentWordNumber +=numWordsInPhrase
    
    # sanity check: 
    if currentWordNumber != len(detectedTokenListNoPauses):
            sys.exit(' number of tokens in annotation {} differs from  num tokens detected {}. No evaluation possible'.format( len(annotationTokenListNoPauses), len(detectedTokenListNoPauses) ) )

    totalLength = max(float(finalTsAnno), float(finalTsDetected)   )       -       initialTimeOffset
    return  durationCorrect, totalLength 


def calcCorrect(detectedTokenListNoPauses, annotationTokenListNoPauses, idx, currentWordNumber, numWordsInPhrase, finallTsAnno, finalTsDetected)  :
#     phrase overlap correct
    currBeginAnno = float(annotationTokenListNoPauses[idx][0])
    currEndAnno = float(annotationTokenListNoPauses[idx][1])

    currBeginDetected  = detectedTokenListNoPauses[currentWordNumber][0]
    currEndDetected = detectedTokenListNoPauses[currentWordNumber + numWordsInPhrase - 1][1]
    
    correct = max(0,min(currEndAnno,currEndDetected) - max(currBeginAnno, currBeginDetected))

#     silence overlap correct
    if idx !=  (len(annotationTokenListNoPauses) - 1):
        nextBeginAnno = float(annotationTokenListNoPauses[idx+1][0])
        
        if currentWordNumber + numWordsInPhrase > len(detectedTokenListNoPauses) -1 :
            sys.exit("length of list of deteceted tokens = {} differes from len of tokens in annotation {}".format(len(detectedTokenListNoPauses),currentWordNumber + numWordsInPhrase ))
        nextBeginDetected = detectedTokenListNoPauses[currentWordNumber + numWordsInPhrase][0]
        correct += max(0,min(nextBeginAnno,nextBeginDetected) - max(currEndAnno, currEndDetected))
    else:
        if (currEndAnno > finalTsDetected):  
            pass
#             sys.exit("currEndAnno > finalTsDetected")
        if (currEndDetected > finallTsAnno ):
            # WORKAROUND
            logging.warn("currEndDetected {} > finallTsAnno {}".format(currEndDetected, finallTsAnno))
            currEndDetected = finallTsAnno
        
        correct += max(0,min(finallTsAnno,finalTsDetected) - max(currEndAnno, currEndDetected))
        
    return correct

