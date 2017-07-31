'''
Created on Jun 30, 2015

@author: joro
'''
from align_eval.WordLevelEvaluator import _evalAlignmentError, tierAliases,\
    stripNonLyricsTokens
from align_eval.PraatVisualiser import ANNOTATION_EXT
import os
from align_eval.AccuracyEvaluator import _evalAccuracy
from mir_eval.io import load_labeled_intervals
import mir_eval
# import mir_eval.display
import matplotlib.pyplot as plt

PATH_TEST_DATASET = '../example/'

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

def evalAccuracy_lab_test():
    '''
    test accuracy of alignment with loading the .lab files 
    '''
    
    plt.figure()
    refs_URI = os.path.join(PATH_TEST_DATASET, 'words.refs')
    ref_intervals, ref_labels = load_labeled_intervals(refs_URI)
    
    
    detected_URI = os.path.join(PATH_TEST_DATASET, 'words.detected')
    detected_intervals, detected_labels = load_labeled_intervals(detected_URI)

#     mir_eval.display.labeled_intervals(ref_int, ref_labels, alpha=0.5, label='Reference')    
#     plt.legend()
#     plt.show()
    initialTimeOffset_refs = ref_intervals[0][0]
    finalts_refs = ref_intervals[-1][1]
    durationCorrect, totalLength  = _evalAccuracy(ref_intervals, detected_intervals, 
                                                  finalts_refs,  initialTimeOffset_refs, ref_labels )
    print durationCorrect / totalLength

def evalAccuracy_TextGird_test():
       
    audioName = '05_Semahat_Ozdenses_-_Bir_Ihtimal_Daha_Var_0_zemin_from_69_5205_to_84_2'
    annotationURI = os.path.join(PATH_TEST_DATASET,  audioName + ANNOTATION_EXT)
     
    # TODO: load from file
#     detectedURI = os.path.join(PATH_TEST_DATASET,  audioName +  '.phrasesDurationAligned')
   
    detected_token_list =   [[0.61, 0.94, u'Bir'], [1.02, 3.41, u'ihtimal'], [3.42, 4.11, u'daha'], [4.12, 5.4, u'var'], \
    [8.03, 8.42, u'o'], [8.46, 8.83, u'da'], [8.86, 10.65, u'\xf6lmek'], [10.66, 11.04, u'mi'], [11.05, 14.39, u'dersin']]
     
    startIndex = 0
    endIndex = -1 
#     alignmentErrors = _evalAlignmentError(annotationURI, detected_token_list, tierAliases.phrases, startIndex, endIndex)
#     print alignmentErrors
    
    
    annotationTokenList, detected_token_list, finalTsAnno, initialTimeOffset = \
     stripNonLyricsTokens(annotationURI, detected_token_list, tierAliases.phrases , startIndex, endIndex)
    
    durationCorrect, totalLength  = _evalAccuracy(annotationTokenList, detected_token_list, 
                                                  finalTsAnno,  initialTimeOffset )
    print durationCorrect / totalLength


if __name__ == '__main__':
#     evalAccuracy_TextGird_test()    
    evalAccuracy_lab_test()
