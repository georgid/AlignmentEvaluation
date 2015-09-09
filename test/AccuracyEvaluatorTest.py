'''
Created on Jun 30, 2015

@author: joro
'''
import os
from AccuracyEvaluator import _evalAccuracy
import sys

# file parsing tools as external lib 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir, os.path.pardir)) 

if parentDir not in sys.path:
      sys.path.append(parentDir)
pathUtils = os.path.join(parentDir, 'utilsLyrics')

from Utilz import  readListOfListTextFile


def evalAccuracyTest():

######### for test logic see WordLevelEvaluator instead

    PATH_TEST_DATASET = '../example/'
      
    annotationURI = os.path.join(PATH_TEST_DATASET,  'grTruth.TextGrid')
    
    #  load from file
#     detectedURI = os.path.join(PATH_TEST_DATASET,  audioName +  '.phrasesDurationAligned')
    detectedTokenList = readListOfListTextFile(os.path.join(PATH_TEST_DATASET,  'detected.aligned'))
    
    
    ###############
    annotationURI = '/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70//laosheng-erhuang_04.TextGrid'
    
    detectedTokenList = readListOfListTextFile('/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/laosheng-erhuang_04_49.8541936425_108.574785469.syllables')
    startIdx=1; endIdx=13
    
    #################
    annotationURI = '/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/laosheng-erhuang_04.TextGrid'
    detectedTokenList = readListOfListTextFile('/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/laosheng-erhuang_04_134.647686205_168.77679257.syllables')
    startIdx=15; endIdx=26

    
    whichTier=3
    durationCorrect, totalLength  = _evalAccuracy(annotationURI, detectedTokenList,whichTier , startIdx, endIdx)
    print durationCorrect
    print totalLength
    print durationCorrect/totalLength

evalAccuracyTest()