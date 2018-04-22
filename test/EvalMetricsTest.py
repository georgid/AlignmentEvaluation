"""
Created on Jun 30, 2015

@author: joro
"""
import sys
import os
from align_eval.Utilz import getMeanAndStDevError
from align_eval.Utilz import load_labeled_intervals

project_dir = os.path.join(os.path.dirname(__file__), '..')

if project_dir not in sys.path:
    sys.path.append(project_dir)

from align_eval.ErrorEvaluator import _evalAlignmentError
from align_eval.ErrorEvaluator import tierAliases
from align_eval.ErrorEvaluator import stripNonLyricsTokens
from align_eval.PraatVisualiser import ANNOTATION_EXT
from align_eval.PercentageCorrectEvaluator import _evalPercentageCorrect
# import mir_eval
# import mir_eval.display
import matplotlib.pyplot as plt

PATH_TEST_DATASET = os.path.join(project_dir, 'example/')

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


def eval_percentage_correct_lab_test(dataset='hansen'):
    """
    test the percentage of duration of correctly aligned tokens with loading the .lab files 
    """
    
    ref_intervals, detected_intervals, ref_labels = load_ref_and_detections(dataset=dataset)
    
    initial_time_offset_refs = ref_intervals[0][0]
    finalts_refs = ref_intervals[-1][1]
    duration_correct, total_length = _evalPercentageCorrect(ref_intervals,
                                                            detected_intervals,
                                                            finalts_refs,
                                                            initial_time_offset_refs,
                                                            ref_labels )

    print("Alignment percentage correct: ",  duration_correct / total_length)


def eval_error_lab_test(dataset='hansen'):
    """
    test mean average error/displacement (in seconds) of alignment with loading the .lab files 
    """
    
    ref_intervals, detected_intervals, ref_labels = load_ref_and_detections(dataset=dataset)

    alignmentErrors = _evalAlignmentError(ref_intervals, detected_intervals, tierAliases.phrases, ref_labels)
    mean, stDev, median = getMeanAndStDevError(alignmentErrors)
    print("Alignment error mean : ", mean, "Alignment error st. dev: ", stDev)


def eval_accuracy_lab_test(dataset='hansen'):
    """
    test the accuracy of tokens with a tolerance window tau loading the .lab files 
    """
    
    ref_intervals, detected_intervals, ref_labels = load_ref_and_detections(dataset=dataset)
    
#     initialTimeOffset_refs = ref_intervals[0][0]
#     finalts_refs = ref_intervals[-1][1]
    
    # TODO:
    accuracy = 1
#     accuracy  = _evalAccuracy(ref_intervals, detected_intervals,
#                                                   finalts_refs,  initialTimeOffset_refs, ref_labels )
    
    print("Alignment accuracy: ",  accuracy)

  
def load_ref_and_detections(dataset='hanson'):
    """
    convenience method. You can test with one example audio and annotation of each of the two datasets
    """
    plt.figure()

    if dataset == 'generic':
        # generic data
        refs_URI = os.path.join(PATH_TEST_DATASET, 'words.refs.lab')
        detected_URI = os.path.join(PATH_TEST_DATASET, 'words.detected.lab')

        # refs_URI = os.path.join(PATH_TEST_DATASET, 'words.onsets.refs.lab')
        # detected_URI = os.path.join(PATH_TEST_DATASET, 'words.onsets.detected.lab')
    elif dataset == 'hansen':
        # for Hansen's dataset
        refs_URI = os.path.join(PATH_TEST_DATASET, 'umbrella_words.refs.lab')  # for Hansen's dataset
        detected_URI = os.path.join(PATH_TEST_DATASET, 'umbrella_words.refs.lab')  # as if reference were detections
    elif dataset == 'mauch':
        # for Mauch's dataset
        refs_URI = os.path.join(PATH_TEST_DATASET, 'Muse.GuidingLight.refs.lab')
        detected_URI = os.path.join(PATH_TEST_DATASET, 'Muse.GuidingLight.refs.lab') # as if reference were detections
    else:
        raise ValueError("{} is not exist.".format(dataset))
    
    ref_intervals, ref_labels = load_labeled_intervals(refs_URI)
    detected_intervals, detected_labels = load_labeled_intervals(detected_URI)
    
    return ref_intervals, detected_intervals, ref_labels
    

def eval_percentage_correct_textgrid_test():
       
    audioName = '05_Semahat_Ozdenses_-_Bir_Ihtimal_Daha_Var_0_zemin_from_69_5205_to_84_2'
    annotationURI = os.path.join(PATH_TEST_DATASET,  audioName + ANNOTATION_EXT)
     
    # TODO: load from file
#     detectedURI = os.path.join(PATH_TEST_DATASET,  audioName +  '.phrasesDurationAligned')
   
    detected_token_list = [[0.61, 0.94, u'Bir'],
                           [1.02, 3.41, u'ihtimal'],
                           [3.42, 4.11, u'daha'],
                           [4.12, 5.4, u'var'],
                           [8.03, 8.42, u'o'],
                           [8.46, 8.83, u'da'],
                           [8.86, 10.65, u'\xf6lmek'],
                           [10.66, 11.04, u'mi'],
                           [11.05, 14.39, u'dersin']]
     
    startIndex = 0
    endIndex = -1 
    
    
    annotationTokenList, detected_token_list, finalTsAnno, initialTimeOffset = \
     stripNonLyricsTokens(annotationURI,
                          detected_token_list,
                          tierAliases.phrases,
                          startIndex,
                          endIndex)
    
    durationCorrect, totalLength  = _evalPercentageCorrect(annotationTokenList,
                                                           detected_token_list,
                                                           finalTsAnno,
                                                           initialTimeOffset)
    print(durationCorrect / totalLength)


def eval_error_textgrid_test():
    
    audioName = '05_Semahat_Ozdenses_-_Bir_Ihtimal_Daha_Var_0_zemin_from_69_5205_to_84_2'
    annotationURI = os.path.join(PATH_TEST_DATASET,  audioName + ANNOTATION_EXT)
    
    startIndex = 0
    endIndex = -1
    
    detected_token_list = [[0.61, 0.94, u'Bir'],
                           [1.02, 3.41, u'ihtimal'],
                           [3.42, 4.11, u'daha'],
                           [4.12, 5.4, u'var'],
                           [8.03, 8.42, u'o'],
                           [8.46, 8.83, u'da'],
                           [8.86, 10.65, u'\xf6lmek'],
                           [10.66, 11.04, u'mi'],
                           [11.05, 14.39, u'dersin']]
    
    annotationTokenList, detected_token_list, dummy, dummy = \
     stripNonLyricsTokens(annotationURI,
                          detected_token_list,
                          tierAliases.phrases,
                          startIndex,
                          endIndex)
     
    alignmentErrors = _evalAlignmentError(annotationTokenList,
                                          detected_token_list,
                                          tierAliases.phrases)
    mean, stDev, median = getMeanAndStDevError(alignmentErrors)
    print("mean : ", mean, "st dev: ", stDev)


if __name__ == '__main__':
    # test alignment error
    #     eval_error_textGrid_test()
    eval_error_lab_test(dataset='hansen')

    # test percentage of correct segments
    #     evalPercentageCorrect_TextGird_test()
    eval_percentage_correct_lab_test(dataset='hansen')
    
    # test accuracy with tolerance t = 1s
    eval_accuracy_lab_test(dataset='hansen')