'''
Created on Oct 4, 2020

@author: Georgi Dzhambazov
@email: info@voicemagix.com
'''
import csv
import os
from align_eval.Utilz import getMeanAndStDevError
from align_eval.eval_summary_MIREX2018 import writeCsv_

URI = '/Users/joro/Dropbox/MIREX2020_results/lt/'

def doit(algorithm_name, dataset_name):
    '''
    read all results on a submission/algorithm on one dataset
    Change the algorithm name and path to annotations
    '''
    

    
#     results_dataset_file = algorithm_name + '/results.csv'
    annotation_URI = os.path.join(URI + dataset_name, algorithm_name, 'results.csv')
    print(annotation_URI)
    WER = []
    ins = []
    dels = []
    subs = []
    words = []
    
    with open(annotation_URI, 'r') as csvfile:
                score_ = csv.reader(csvfile, delimiter=',')
                for i,row in enumerate(score_): # each row is a song
                    if i == 0:
                        continue
                    if algorithm_name == 'DDA2' or algorithm_name == 'DDA3':
                        WER.append( 100* (float(row[1])) )
                    else:
                        WER.append( (float(row[1])) )
                    ins.append( (float(row[2])) )
                    dels.append( (float(row[3])) )
                    subs.append( (float(row[4])) )
                    words.append( (float(row[5])) )
                    
    mean_WER,  stdevE, medianE = getMeanAndStDevError(WER)
    mean_ins,  stdevE, medianE = getMeanAndStDevError(ins)
    mean_dels, stdevP, medianP = getMeanAndStDevError(dels)
    mean_subs, stdevP, medianP = getMeanAndStDevError(subs)
    mean_words, stdevP, medianP = getMeanAndStDevError(words)
    
    ############ Append to summary for a dataset #########################               
    
    result_summary_file = 'summary_' + dataset_name + '.csv'
    output_URI = os.path.join(URI + dataset_name, result_summary_file)
    results = [[algorithm_name,'{:.2f}'.format(mean_WER), '{:.2f}'.format(mean_ins), '{:.2f}'.format(mean_dels) ,  '{:.2f}'.format(mean_subs), '{:.2f}'.format(mean_words)] ]

    if not os.path.exists(output_URI):
        results_prefix = [['Submission', 'WER','Insertions','Deletions','Substitutions','TotalWords']]
        writeCsv_(output_URI, results_prefix, append=0)
        writeCsv_(output_URI, results, append=1)
        print ( 'file {} written'.format(output_URI))

    else:
        print ( 'Appended to file {}'.format(output_URI))
        writeCsv_(output_URI, results, append=1)


if __name__ == '__main__':
    
    algorithm_names = ['GGL1', 'GGL2','RB1', 'DDA2', 'DDA3']

    
    dataset_name = 'HansensDataset_acappella'    
#     dataset_name = 'HansensDataset'
#     dataset_name = 'MauchsDataset'
#     dataset_name = 'Gracenote'
#     dataset_name = 'jamendolyrics'

    for algorithm_name in algorithm_names:
        doit(algorithm_name, dataset_name)
    