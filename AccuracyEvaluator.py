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

def evalAccuracy(URIrecordingAnno, outputHTKPhoneAlignedURI, whichLevel=2 ):
    
    detectedTokenList = loadDetectedTokenListFromMlf( outputHTKPhoneAlignedURI, whichLevel )
    durationCorrect, totalDuration = _evalAccuracy(URIrecordingAnno, detectedTokenList, whichLevel)
    return  durationCorrect, totalDuration 

def _evalAccuracy(annotationURI, detectedTokenList, whichLevel=2, beginTsOffsetAnnotaion=0 ):
    '''
Calculate accuracy as suggested in
Fujihara paper
Does not check token identities, but proceeds successively one-by-one  
Make sure number of detected tokens (wihtout counting sp, sil ) is same as number of annotated tokens 

    @param detectedURI: a list of triples: (startTs, endTs, wordID) 
    @param annotationURI: URI of Praat annotaiton textgrid. 
    @param whichLevel, 0- phonemeLevel, 1 -wordLevel,  2 - phraseLevel. The level at which to compare phrases 
    reads only the layer from with name correspondingly phonemes, words or phrases
    
    token: could be phoneme (consists of one subtoken -phoneme itself), word (consists of one subtoken -word itself) or phrase (consist of subtokens words ) 

TODO: eval performance of end timest. only and compare with begin ts. 

    '''
    
        ######################  
    annotationTokenListNoPauses, detectedTokenListNoPauses = stripNonLyricsTokens(annotationURI, detectedTokenList, whichLevel)
    


    durationCorrect = 0;

    if len(annotationTokenListNoPauses) == 0:
        logging.warn(annotationURI + ' is empty! Check code')
        return durationCorrect
    
    
    if len(detectedTokenListNoPauses) == 0:
        logging.warn(' detected token list is empty! Check code')
        return durationCorrect
    
    # loop in tokens of gr truth annotation
    durationCorrect = min(float(annotationTokenListNoPauses[0][0]), detectedTokenListNoPauses[0][0])
    
    currentWordNumber = 0
    for idx, currAnnoTsAndToken in enumerate(annotationTokenListNoPauses):
       
        currAnnoTsAndToken[2] = currAnnoTsAndToken[2].strip()
        subtokens = currAnnoTsAndToken[2].split()
        numWordsInPhrase = len(subtokens)
        
        if numWordsInPhrase == 0:
            sys.exit('token (phrase) with no subtokens (words) in annotation file!')
        
        if  currentWordNumber >= len(detectedTokenListNoPauses):
            sys.exit(' number of tokens in annotation {} differs from  num tokens detected {}. No evaluation possible \n Detection: {} '\
                     .format( currentWordNumber, len(detectedTokenListNoPauses), detectedTokenListNoPauses))
            
        
        durationCorrectCurr =  calcCorrect(detectedTokenListNoPauses, annotationTokenListNoPauses, idx, currentWordNumber, numWordsInPhrase,  beginTsOffsetAnnotaion)        
        durationCorrect += durationCorrectCurr
        
        #### UPDATE: proceed in detection the number of subtokens in current token          
        currentWordNumber +=numWordsInPhrase
    
    # sanity check: 
    if currentWordNumber != len(detectedTokenListNoPauses):
            sys.exit(' number of tokens in annotation {} differs from  num tokens detected {}. No evaluation possible'.format( currentWordNumber, len(detectedTokenListNoPauses)))

    totalLength = float(annotationTokenListNoPauses[-1][1])
    return  durationCorrect, totalLength


def calcCorrect(detectedTokenListNoPauses, annotationTokenListNoPauses, idx, currentWordNumber, numWordsInPhrase, beginTsOffsetAnnotaion=0)  :
#     phrase overlap correct
    currBeginAnno = float(annotationTokenListNoPauses[idx][0]) + beginTsOffsetAnnotaion
    currEndAnno = float(annotationTokenListNoPauses[idx][1]) + beginTsOffsetAnnotaion
    finallTsAnno = float(annotationTokenListNoPauses[-1][1]) + beginTsOffsetAnnotaion

    currBeginDetected  = detectedTokenListNoPauses[currentWordNumber][0]
    currEndDetected = detectedTokenListNoPauses[currentWordNumber + numWordsInPhrase - 1][1]
    finalTsDetected = detectedTokenListNoPauses[-1][1]
    
    
    correct = max(0,min(currEndAnno,currEndDetected) - max(currBeginAnno, currBeginDetected))

#     silence overlap correct
    if idx <  (len(annotationTokenListNoPauses) - 1):
        nextBeginAnno = float(annotationTokenListNoPauses[idx+1][0])
        
        if currentWordNumber + numWordsInPhrase > len(detectedTokenListNoPauses) - 1 :
            sys.exit("Error in avaluation. to do implement")
        nextBeginDetected = detectedTokenListNoPauses[currentWordNumber + numWordsInPhrase][0]
        correct += max(0, min(nextBeginAnno,nextBeginDetected) - max(currEndAnno, currEndDetected))
    else:
        if (currEndAnno > finalTsDetected):  
            logging.warning("currEndAnno > finalTsDetected")
        if (currEndDetected > finallTsAnno ):
            # WORKAROUND
            logging.warn("currEndDetected {} > finallTsAnno {}. Making currEndDetected = finallTsAnno ".format(currEndDetected, finallTsAnno))
            currEndDetected = finallTsAnno
        
        correct += max(0,min(finallTsAnno,finalTsDetected) - max(currEndAnno, currEndDetected))
    
       
    return correct


if __name__ == '__main__':


    PATH_TEST_DATASET = 'example/'
      
    annotationURI = os.path.join(PATH_TEST_DATASET,  'grTruth.TextGrid')
    
    #  load from file
#     detectedURI = os.path.join(PATH_TEST_DATASET,  audioName +  '.phrasesDurationAligned')
    detectedTokenList = readListOfListTextFile(os.path.join(PATH_TEST_DATASET,  'detected.aligned'))

    
    
    durationCorrect, totalLength  = _evalAccuracy(annotationURI, detectedTokenList, whichLevel=2 )
    print durationCorrect / totalLength