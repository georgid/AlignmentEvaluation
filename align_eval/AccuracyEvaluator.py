'''
Created on Feb 24, 2015

@author: joro
'''
from align_eval.WordLevelEvaluator import stripNonLyricsTokens,\
    loadDetectedTokenListFromMlf
import logging
import sys
import os

# file parsing tools as external lib 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 

# pathUtils = os.path.join(parentDir, 'utilsLyrics')
# sys.path.append(pathUtils )
# from utilsLyrics.Utilz import  readListOfListTextFile

def evalAccuracy(annotationURI, outputHTKPhoneAlignedURI, whichTier, startIdx, endIdx ):
    '''
    Wrapper around _evalAccuracy() for txt file outputHTKPhoneAlignedURI
    
    Parameters
    --------------
    outputHTKPhoneAlignedURI: detected timestamps in htk's mlf format 
    
    other parameters same as in _evalAccuracy
    '''
    
    detectedTokenList = loadDetectedTokenListFromMlf( outputHTKPhoneAlignedURI, whichTier )
    
    annotationTokenList, detectedTokenList, finalTsAnno,  initialTimeOffset = \
     stripNonLyricsTokens(annotationURI, detectedTokenList, whichTier, startIdx, endIdx)
    
    durationCorrect, totalDuration = _evalAccuracy(annotationTokenList, detectedTokenList, finalTsAnno,  initialTimeOffset)
    return  durationCorrect, totalDuration 



def split_into_tokens(tokens):
    '''
    split phrases of tokens by white spaces into words 
    '''
    
    idx_txt = -1 # assume the word is the last entry of a token (after begin timestamp etc.)
    num_tokens_in_phrase = []
    for currAnnoTsAndToken in tokens:
        if  type(currAnnoTsAndToken) == str:
            txt = currAnnoTsAndToken
        else:
            txt = currAnnoTsAndToken[idx_txt]
        txt = txt.strip()
        subtokens = txt.split()
        numWordsInPhrase = len(subtokens)
        if numWordsInPhrase == 0:
            sys.exit('token (phrase) with no subtokens (words) in annotation file!')
        num_tokens_in_phrase.append(numWordsInPhrase)
    
    return num_tokens_in_phrase, currAnnoTsAndToken

def _evalAccuracy(reference_token_list, detected_Token_List, finalTsAnno, initialTimeOffset=0, reference_labels=None):
    '''
    Calculate accuracy as suggested in
    Fujihara: LyricSynchronizer: Automatic Synchronization System Between Musical Audio Signals and Lyrics
    Does not check token identities, but proceeds successively one-by-one  
    Make sure number of detected tokens not counting special tokens (sp, sil ) is same as number of annotated tokens 

    token: could be phoneme (consists of one subtoken -phoneme itself),
    word (consists of one subtoken -word itself) or 
    phrase (consist of subtokens words ) 


    Parameters
    -------------- 
    detected_Token_List: list [[]]
        a list of triples: (startTs, endTs, wordID) 
    
    reference_token_list: string
        URI of Praat annotaiton textgrid file
    
    
    '''
    
    # WoRKAROUND. because currenty I dont store final sil in detected textFile .*Aligned 
#     finalTsDetected = finalTsAnno

    durationCorrect = 0;

    if len(reference_token_list) == 0:
        logging.warn(reference_token_list + ' is empty! Check code')
        return durationCorrect

    if len(detected_Token_List) == 0:
        logging.warn(' detected token list is empty! Check code')
        return durationCorrect
    
    ##########  divide phrases into tokens
    if reference_labels != None: # labels of reference tokens given separately 
        num_tokens_in_phrase, currAnnoTsAndToken = split_into_tokens(reference_labels)
    else: # labels should be the last field of reference_token_list
        num_tokens_in_phrase, currAnnoTsAndToken = split_into_tokens(reference_token_list)
    

    ##### check that annotation and detection have same number of tokens
    if sum(num_tokens_in_phrase) != len(detected_Token_List):
            sys.exit(' number of tokens in annotation {} differs from  num tokens detected {}. No evaluation possible \n Detection: {} \n Annotation: {}'\
                     .format( sum(num_tokens_in_phrase), len(detected_Token_List), detected_Token_List, reference_token_list))
    
    # initialize initial time offset
    durationCorrect = min(float(reference_token_list[0][0]), detected_Token_List[0][0]) - initialTimeOffset
    # evaluate: loop in tokens of gr truth annotation

    #     finalTsDetected = detectedTokenList[-1][0][1] # a word has one syllable
    finalTsDetected = detected_Token_List[-1][1]

    currentWordNumber = 0
    for idx, currAnnoTsAndToken in enumerate(reference_token_list):
        
        durationCorrectCurr = calcCorrect(detected_Token_List, reference_token_list, \
                            idx, currentWordNumber,  num_tokens_in_phrase[idx], finalTsAnno, finalTsDetected)         
        durationCorrect += durationCorrectCurr
        
        #### UPDATE: proceed in detection the number of subtokens in current token          
        currentWordNumber += num_tokens_in_phrase[idx]
    
    
    
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

