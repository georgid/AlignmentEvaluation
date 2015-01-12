'''
Tools to parse output of alignment and visualise results in Praat 
Created on Nov 27, 2014

@author: joro
'''
import sys
import os
import logging
import shutil
import subprocess

# change path to where Praat is installed
PATH_TO_PRAAT = '/Applications/Praat.app/Contents/MacOS/Praat'

parentDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__ ) ) )
PATH_TO_PRAAT_SCRIPT= os.path.join(parentDir, 'loadAlignedResultAndTextGrid.rb')

print PATH_TO_PRAAT_SCRIPT

HTK_MLF_ALIGNED_SUFFIX= ".htkAlignedMlf"
 
# in textual column-like format (e.g. timestamp \t word)
WORD_ALIGNED_SUFFIX= ".wordAligned"
PHONEME_ALIGNED_SUFFIX= ".phonemeAligned"

PHRASE_ANNOTATION_EXT = '.TextGrid'

# utils to do reading and writing into text files  
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
pathUtils = os.path.join(parentDir, 'utilsLyrics')
sys.path.append(pathUtils )

from Utilz import writeListOfListToTextFile, loadTextFile 
   
def prepareOutputForPraat(outputHTKPhoneAlignedURI, timeShift):
        '''
        parse output in HTK's mlf output format ; load into list; 
        serialize into table format easy to load from praat: 
        -in word-level 
        and 
        - phoneme level
        
        '''    
    ################ parse mlf and write word-level text file    
       
        listTsAndWords = mlf2WordAndTsList(outputHTKPhoneAlignedURI)
        
        
        baseNameAudioFile = os.path.splitext(outputHTKPhoneAlignedURI)[0]
        wordAlignedfileName=  mlf2PraatFormat(listTsAndWords, timeShift, baseNameAudioFile, WORD_ALIGNED_SUFFIX)
    
      
    ########################## same for phoneme-level: 
        
        # with : phoneme-level alignment
        listTsAndPhonemes = mlf2PhonemesAndTsList (outputHTKPhoneAlignedURI)
        phonemeAlignedfileName=  mlf2PraatFormat(listTsAndPhonemes, timeShift, baseNameAudioFile, PHONEME_ALIGNED_SUFFIX)
        
        
        
        return wordAlignedfileName, phonemeAlignedfileName


def mlf2PraatFormat( listTsAndPhonemes, timeShift, baseNameAudioFile, whichSuffix):
    '''
    convenience method
    '''
    
    # timeshift
    for index in range(len(listTsAndPhonemes)):
        listTsAndPhonemes[index][0] = listTsAndPhonemes[index][0] + timeShift
#         if (len(listTsAndPhonemes[index]) == 3): 
#             del listTsAndPhonemes[index][1]
        
    phonemeAlignedfileName = baseNameAudioFile + whichSuffix
    
    writeListOfListToTextFile(listTsAndPhonemes, 'startTs endTs phonemeOrWord\n', phonemeAlignedfileName)
    logging.debug('phoneme level alignment written to file: ',  phonemeAlignedfileName)
    return phonemeAlignedfileName

    
    
def addAlignmentResultToTextGrid(detectedTokenList,  wordAnnoURI, pathToAudioFile, tierNameWordAligned, tierNamePhonemeAligned):
    '''
    same as addAlignmentResultToTextGridFIle, but
    instead of file with outputHTKPhoneAlignedURI use python list: @param detectedTokenList
    '''
    baseNameAudioFile = os.path.splitext(pathToAudioFile)[0]
    wordAlignedfileName=  mlf2PraatFormat(detectedTokenList, 0, baseNameAudioFile, WORD_ALIGNED_SUFFIX)
    alignedResultPath, fileNameWordAnno = _alignmentResult2TextGrid(wordAnnoURI,wordAlignedfileName, tierNameWordAligned, tierNamePhonemeAligned, 0)  
    return alignedResultPath, fileNameWordAnno               


def addAlignmentResultToTextGridFIle( outputHTKPhoneAlignedURI, wordAnnoURI, tierNameWordAligned, tierNamePhonemeAligned):
    '''
    called when HTK used and output written in mlf file
    '''
    timeShift= 0
    
    wordAlignedfileName, phonemeAlignedfileName = prepareOutputForPraat(outputHTKPhoneAlignedURI, timeShift)
    
    alignedResultPath, fileNameWordAnno = _alignmentResult2TextGrid(wordAnnoURI,wordAlignedfileName,  tierNameWordAligned, tierNamePhonemeAligned)
    return alignedResultPath, fileNameWordAnno 
    

    '''
    call Praat script to: 
    -open phoneLevel.annotation file  .TextGrid
    -open the result alignemnt  
    -add the result as tier in the TextGrid
    -save the new file as .comparison.TextGrid
    
    '''
    
def _alignmentResult2TextGrid(wordAnnoURI, wordAlignedfileName, tierNameWordAligned, tierNamePhonemeAligned ):
    
     
    ########### call praat script to add alignment as a new layer to existing annotation TextGrid
    alignedResultPath = os.path.dirname(wordAlignedfileName)
    alignedFileBaseName = os.path.splitext(os.path.basename(wordAlignedfileName))[0]
    
    
    # copy  annotation TExtGrid to path of results
    
    dirNameAnnotaion = os.path.dirname(wordAnnoURI)
    if (dirNameAnnotaion != alignedResultPath):
        shutil.copy2(wordAnnoURI,alignedResultPath )

    fileNameWordAnno = os.path.splitext(os.path.basename(wordAnnoURI))[0]
    
    # in praat script extensions  WORD_ALIGNED_SUFFIX  is added automatically
    command = [PATH_TO_PRAAT, PATH_TO_PRAAT_SCRIPT, alignedResultPath, fileNameWordAnno,  alignedFileBaseName, WORD_ALIGNED_SUFFIX, tierNameWordAligned ]
    pipe = subprocess.Popen(command)
    pipe.wait()
    
    # same praat script for PHONEME_ALIGNED_SUFFIX
    command = [ PATH_TO_PRAAT, PATH_TO_PRAAT_SCRIPT, alignedResultPath, fileNameWordAnno,  alignedFileBaseName, PHONEME_ALIGNED_SUFFIX, tierNamePhonemeAligned ]
    pipe =subprocess.Popen(command)
    pipe.wait()
    
    return alignedResultPath, fileNameWordAnno
    
    
def openTextGridInPraat(alignedResultPath, fileNameWordAnno, pathToAudioFile):
    '''     open Praat to visualize it (done for MAC OS X)
    '''
    
    comparisonTextGridURI =  os.path.join(alignedResultPath, fileNameWordAnno)  + PHRASE_ANNOTATION_EXT
    pipe = subprocess.Popen(["open", '-a', PATH_TO_PRAAT, comparisonTextGridURI])
    pipe.wait()
    
    # and audio

    pipe = subprocess.Popen(["open", '-a', PATH_TO_PRAAT, pathToAudioFile])
    pipe.wait()



def mlf2PhonemesAndTsList(inputFileName):
    '''
    parse output of alignment in mlf format ( with words) 
    output: phonemes with begin and end ts 
    
    # TODO: change automatically extension from txt to mlf
    
    ''' 
    
    allLines = loadTextFile(inputFileName)
    
    
    listPhonemesAndTs = []
    prevStartTime = -1    
    
    
    # when reading lines from MLF, skip first 2 and last
    for line in allLines[2:-1]:
        
        tokens =  line.split(" ")

        startTime = float(tokens[0])/10000000
        
        endTime = float(tokens[1])/10000000
        
        # if Praat does not allow insertion of new token with same timestamp. This happend when prev. token was 'sp'. So remove it and insert current
        if (prevStartTime == startTime):
            listPhonemesAndTs.pop()
            
        
        phoneme = tokens[2].strip()
        
        
        listPhonemesAndTs.append([startTime,endTime,  phoneme])
        
        # remember startTime 
        prevStartTime = startTime
         
    return listPhonemesAndTs
    
    

    
def mlf2WordAndTsList(inputFileName):
        
    '''
    parse output of alignment in mlf format ( with words) 
    output: words with begin and end ts 
    NOTE: length of tokens=5 if no -o option is set on HVite
    TODO: change automatically extension from txt to mlf
    ''' 
    
    extracedWordList = []
    
    LENGTH_TOKENS_NEW_WORD= 5
    
    allLines = loadTextFile(inputFileName)
    
    listWordsAndTs = allLines[2:-1]
        
    currentTokenIndex = 0    
    tokens =  listWordsAndTs[currentTokenIndex].split(" ")
    
    while currentTokenIndex < len(listWordsAndTs):
        
        # get begin ts 
        startTime = float(tokens[0])/10000000
        wordMETU = tokens[-1].strip()
        
        # move to next        
        prevTokens = tokens 
        currentTokenIndex += 1
        
        # sanity check
        if currentTokenIndex >= len(listWordsAndTs):
            endTime =  float(prevTokens[1])/10000000
            extracedWordList.append([startTime, endTime, wordMETU])     
 
            break
        
        tokens =  listWordsAndTs[currentTokenIndex].split(" ")
        
        # fast forward phonemes while end of word
        while len(tokens) == LENGTH_TOKENS_NEW_WORD - 1 and currentTokenIndex < len(listWordsAndTs):
            
            # end of word is last phoneme before 'sp' 
            if tokens[2]=="sp":
                # move to next
                currentTokenIndex += 1
                if currentTokenIndex < len(listWordsAndTs):
                    tokens =  listWordsAndTs[currentTokenIndex].split(" ")

                break
            
            prevTokens = tokens 
            currentTokenIndex += 1
            tokens =  listWordsAndTs[currentTokenIndex].split(" ")
        
        # end of word. after inner while loop  
        endTime =  float(prevTokens[1])/10000000
        
        extracedWordList.append([startTime, endTime, wordMETU])     
        
    return extracedWordList    
    