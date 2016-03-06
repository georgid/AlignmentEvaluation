'''
Created on Jun 30, 2015

@author: joro
'''
from WordLevelEvaluator import _evalAlignmentError, tierAliases
from PraatVisualiser import ANNOTATION_EXT
import os


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

def testOneFile():
    PATH_TEST_DATASET = '../example/'
       
    audioName = '05_Semahat_Ozdenses_-_Bir_Ihtimal_Daha_Var_0_zemin_from_69_5205_to_84_2'
    annotationURI = os.path.join(PATH_TEST_DATASET,  audioName + ANNOTATION_EXT)
     
    # TODO: load from file
#     detectedURI = os.path.join(PATH_TEST_DATASET,  audioName +  '.phrasesDurationAligned')
   
    detectedList =   [[0.61, 0.94, u'Bir'], [1.02, 3.41, u'ihtimal'], [3.42, 4.11, u'daha'], [4.12, 5.4, u'var'], [5.5, 7.93, '_SAZ_'], \
    [8.03, 8.42, u'o'], [8.46, 8.83, u'da'], [8.86, 10.65, u'\xf6lmek'], [10.66, 11.04, u'mi'], [11.05, 14.39, u'dersin']]
     
    startIndex = 0
    endIndex = -1 
    alignmentErrors = _evalAlignmentError(annotationURI, detectedList, tierAliases.phrases, startIndex, endIndex)
    print alignmentErrors
         
#     print  mean, " ", stDev



if __name__ == '__main__':
    testOneFile()    
