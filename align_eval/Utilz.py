'''
Created on Jul 30, 2017

These scripts are copued from https://github.com/georgid/AlignmentDuration/blob/noteOnsets/src/utilsLyrics/Utilz.py
in order to reduce inter-porject dependency, please if you modify them, make sure they are updated in the original place
@author: joro
'''
import codecs
import numpy as np
import warnings

import logging
from mir_eval.io import load_delimited
from mir_eval import util
import os
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)


def get_duration_audio(filename):
    '''
    get duration in seconds of .wav file 
    '''
    import wave
    import contextlib
    with contextlib.closing(wave.open(filename,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration


def load_labeled_intervals(filename, delimiter=r'\s+'):
    '''
    overwrites https://github.com/craffel/mir_eval/blob/master/mir_eval/io.py#L208
    in order to be able to change the converters arguments of load_delimieted  to handle , instead of . in floating point vals 
    '''
    # Use our universal function to load in the events
    
    converter_comma = lambda val: float(val.replace(',', '.')) # replace ',' by '.'
    try: # start times and end times given
        starts, ends, labels = load_delimited(filename, [converter_comma, converter_comma, str],
                                          delimiter)
    except Exception, e: # only start times given
        starts,  labels = load_delimited(filename, [converter_comma, str],
                                          delimiter)
        filename_wav = filename[:-9] +'.wav'  # remove .refs.lab and replace it with .wav. TODO make this logic clearer 
        if os.path.isfile(filename_wav):
            duration = get_duration_audio(filename_wav) # generate end timestamps from following start timestamps
        else:
            duration = starts[-1] + 1 # fake last word to be 1 sec long
        ends = starts[1:]; ends.append(duration) 
    # Stack into an interval matrix
    intervals = np.array([starts, ends]).T
    # Validate them, but throw a warning in place of an error
    try:
        util.validate_intervals(intervals)
    except ValueError as error:
        warnings.warn(error.args[0])

    return intervals, labels


def loadTextFile( pathToFile):
        '''
        helper method to load all lines from a text file 
        '''
        
        # U means cross-platform  end-line character
        inputFileHandle = codecs.open(pathToFile, 'rU', 'utf-8')
        
        allLines = inputFileHandle.readlines()

        
        inputFileHandle.close()
        
        return allLines
    
    
def writeListOfListToTextFile(listOfList,headerLine, pathToOutputFile, toFlip=False):    
    outputFileHandle = codecs.open(pathToOutputFile, 'w', 'utf-8')
    
    if not headerLine == None:
        outputFileHandle.write(headerLine)
    
    # flip (transpose) matrix
    if toFlip:
        a = np.rot90(listOfList)
        listOfList = np.flipud(a)
    
    for listLine in listOfList:
        
        output = ""
        for element in listLine:
            outputFileHandle.write("{:35}\t".format(element))
#             output = output + str(element) + "\t"
#         output = output.strip()
#         output = output + '\n'
#         outputFileHandle.write(output)
        outputFileHandle.write('\n')    
    
    outputFileHandle.close()
    
    logger.info ("successfully written file: \n {} \n".format( pathToOutputFile))


def writeCsv(fileURI, list_, withListOfRows=1, append=0):
    '''
    TODO: move to utilsLyrics
    '''
    from csv import writer
    if append:
        fout = open(fileURI, 'ab')
    else:
        fout = open(fileURI, 'wb')
    w = writer(fout)
    print 'writing to csv file {}...'.format(fileURI)
    for row in list_:
        if withListOfRows:
            w.writerow(row)
        else:
            tuple_note = [row.onsetTime, row.noteDuration]
            w.writerow(tuple_note)
    
    fout.close()


def getMeanAndStDevError(alignmentErrors):
    '''
    statistics for an array
    '''
        
    # convert to np array
    absalignmentErrors = [0] * len(alignmentErrors)
    for index, alError in enumerate(alignmentErrors):
        absalignmentErrors[index] = abs(alError)
    
    # calculate with numpy
    mean = np.round(np.mean(absalignmentErrors), decimals=2)
    median = np.round( np.median(absalignmentErrors), decimals=2)
    stDev = np.round( np.std(alignmentErrors), decimals=2)
    
    return mean, stDev, median