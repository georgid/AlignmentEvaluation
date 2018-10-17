'''
Created on Oct 4, 2018

@author: Georgi Dzhambazov
@email: info@voicemagix.com
'''
import csv
import numpy as np
import os
from align_eval.Utilz import getMeanAndStDevError


def doit():
    '''
    read all results ona submission/algorithm on one dataset
    Change the algorithm name and path to annotations
    '''
    
    algorithm_name = 'GSLW3'
    
    dataset_name = 'hansen_clean'
    dataset_path  = '/hansen/clean/'
    
    dataset_name = 'hansen_mix'
    dataset_path  = '/hansen/mix/'
    
    dataset_name = 'mauch'
    dataset_path  = '/mauch/'
    
    # dataset_name = 'gracenote'
    # dataset_path  = '/gracenote/'
    
    annotation_URI = 'MIREX_2018_ala' + dataset_path  + algorithm_name + '_' + dataset_name +'.csv'
    errors = []
    percentages = []
    percentages_e = []
    
    with open(annotation_URI, 'r') as csvfile:
                score_ = csv.reader(csvfile, delimiter=',')
                for i,row in enumerate(score_): # each row is a song
                    if i == 0:
                        continue
                    errors.append( (float(row[1])) )
                    percentages.append( (float(row[2])) )
                    percentages_e.append( (float(row[3])) )
                    
    meanE,  stdevE, medianE = getMeanAndStDevError(errors)
    meanP, stdevP, medianP = getMeanAndStDevError(percentages)
    meanPE, stdevP, medianP = getMeanAndStDevError(percentages_e)
    
    ############ Write summary for a dataset #########################               
    
    
    output_URI = 'MIREX_2018_ala/'+ dataset_path + '/summary_' + dataset_name + '.csv'
    if not os.path.exists(output_URI):
           pass
    else:
            results = [[algorithm_name,'{:.2f}'.format(meanE), '{:.2f}'.format(meanP) ,  '{:.2f}'.format(meanPE)] ]
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
    doit()
    