'''
Created on Oct 10, 2017

@author: joro
'''


import sys
import os
import glob
projDir = os.path.join(os.path.dirname(__file__), os.path.pardir)

if projDir not in sys.path:
    sys.path.append(projDir)

from align_eval.PercentageCorrectEvaluator import _evalPercentageCorrect
from align_eval.Utilz import load_labeled_intervals, getMeanAndStDevError,\
    writeCsv
from parse.TextGrid_Parsing import tierAliases
from align_eval.ErrorEvaluator import _evalAlignmentError



def eval_all_metrics_lab(refs_URI, detected_URI):
    '''
    run all eval metrics on one file
    '''
    ref_intervals, ref_labels = load_labeled_intervals(refs_URI)
    detected_intervals, detected_labels = load_labeled_intervals(detected_URI)
    
    alignmentErrors = _evalAlignmentError(ref_intervals, detected_intervals, tierAliases.phrases, ref_labels)
    mean, stDev, median = getMeanAndStDevError(alignmentErrors)
#     print "Alignment error mean : ", mean, "Alignment error st. dev: " , stDev
    
    ###### percentage correct
    initialTimeOffset_refs = ref_intervals[0][0]
    finalts_refs = ref_intervals[-1][1]
    durationCorrect, totalLength  = _evalPercentageCorrect(ref_intervals, detected_intervals, 
                                                  finalts_refs,  initialTimeOffset_refs, ref_labels )
    percentage_correct = durationCorrect / totalLength
    return mean, percentage_correct


def main_eval_one_file(argv):
    if len(argv) != 3:
        sys.exit('usage: {} <path to reference word boundaries> <path to detected word boundaries> '.format(sys.argv[0]))
    refs_URI = argv[1]
    detected_URI = argv[2]
    
    print 'evaluating on {}'.format(refs_URI) 
    meanError, percentage = eval_all_metrics_lab(refs_URI, detected_URI)
    return meanError, percentage

def main_eval_all_files(argv):
    if len(argv) != 4:
        sys.exit('usage: {} <path dir with to reference word boundaries> <path to dir with detected word boundaries> <path_output>'.format(sys.argv[0]))
    refs_dir_URI = argv[1]
    detected_dir_URI = argv[2]
    a = os.path.join(detected_dir_URI, "*.lab")
    lab_files = glob.glob(a)
    
    results = [['Track', 'Average absolute error'    , 'Percentage of correct segments']]
    for lab_file in lab_files:
        base_name = os.path.basename(lab_file)
        
        ref_file = os.path.join(refs_dir_URI, base_name[:-4] + '.wordonset.tsv')
        mean, percentage = main_eval_one_file(["dummy",  ref_file, lab_file])
        results.append([base_name[:-4],'{:.3f}'.format(mean), '{:.3f}'.format(percentage)])
    output_URI = argv[3]
    writeCsv(os.path.join(output_URI, 'results.csv'), results)
    
if __name__ == '__main__':
#     main_eval_one_file(sys.argv)
    main_eval_all_files(sys.argv)