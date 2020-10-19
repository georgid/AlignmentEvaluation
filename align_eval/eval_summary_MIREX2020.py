'''
Created on Oct 4, 2018

@author: Georgi Dzhambazov
@email: info@voicemagix.com
'''
import csv
import numpy as np
import os
from align_eval.Utilz import getMeanAndStDevError

URI = '/Users/joro/Dropbox/MIREX2020_results/ala/'

def doit(algorithm_name, dataset_name):
    '''
    read all results on a submission/algorithm on one dataset
    Change the algorithm name and path to annotations
    '''
    

    
#     results_dataset_file = algorithm_name + '/results.csv'
    annotation_URI = os.path.join(URI + dataset_name, algorithm_name, 'results.csv')
    print(annotation_URI)
    errors = []
    median_errors = []
    percentages = []
    percentages_e = []
    
    with open(annotation_URI, 'r') as csvfile:
                score_ = csv.reader(csvfile, delimiter=',')
                for i,row in enumerate(score_): # each row is a song
                    if i == 0:
                        continue
                    errors.append( (float(row[1])) )
                    median_errors.append( (float(row[2])) )
                    if dataset_name == 'HansensDataset' or dataset_name =='HansensDataset_acappella':
                        percentages.append( (float(row[3])) ) # TODO: check if NaN
                    percentages_e.append( (float(row[4])) )
                    
    meanE,  stdevE, medianE = getMeanAndStDevError(errors)
    meanMedE,  stdevE, medianE = getMeanAndStDevError(median_errors)
    if dataset_name == 'HansensDataset' or dataset_name =='HansensDataset_acappella':
        meanP, stdevP, medianP = getMeanAndStDevError(percentages)
    meanPE, stdevP, medianP = getMeanAndStDevError(percentages_e)
    
    ############ Append to summary for a dataset #########################               
    
    result_summary_file = 'summary_' + dataset_name + '.csv'
    output_URI = os.path.join(URI + dataset_name, result_summary_file)
    if dataset_name == 'HansensDataset' or dataset_name =='HansensDataset_acappella':
        results = [[algorithm_name,'{:.2f}'.format(meanE), '{:.2f}'.format(meanMedE), '{:.2f}'.format(meanP) ,  '{:.2f}'.format(meanPE)] ]
    else:
        results = [[algorithm_name,'{:.2f}'.format(meanE), '{:.2f}'.format(meanMedE), 'NA' ,  '{:.2f}'.format(meanPE)] ]

    if not os.path.exists(output_URI):
        results_prefix = [['Submission', 'Average absolute error', 'Median absolute error', 'Percentage of correct segments', 'Percentage of correct onsets with tolerance']]
        writeCsv_(output_URI, results_prefix, append=0)
        writeCsv_(output_URI, results, append=1)
        print ( 'file {} written'.format(output_URI))

    else:
        print ( 'Appended to file {}'.format(output_URI))
        writeCsv_(output_URI, results, append=1)


def writeCsv_(fileURI, list_, withListOfRows=1, append=0):
    '''
    TODO: move to utilsLyrics
    '''
    from csv import writer
    if append:
        fout = open(fileURI, 'a')
    else:
        fout = open(fileURI, 'w')
    w = writer(fout)
    print('writing to csv file {}...'.format(fileURI) )
    for row in list_:
        if withListOfRows:
            w.writerow(row)
        else:
            tuple_note = [row.onsetTime, row.noteDuration]
            w.writerow(tuple_note)
    
    fout.close()


if __name__ == '__main__':
    
    algorithm_names = ['GGL1', 'GGL2','ZWZL1', 'ZWZL2', 'ZWZL3', 'DDA1']

    
    dataset_name = 'HansensDataset_acappella'    
    dataset_name = 'HansensDataset'
    dataset_name = 'MauchsDataset'
#     dataset_name = 'Gracenote'
    dataset_name = 'jamendolyrics'

    for algorithm_name in algorithm_names:
        doit(algorithm_name, dataset_name)
    