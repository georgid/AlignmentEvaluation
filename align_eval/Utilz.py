'''
Created on Jul 30, 2017

These scripts are copued from https://github.com/georgid/AlignmentDuration/blob/noteOnsets/src/utilsLyrics/Utilz.py
in order to reduce inter-porject dependency, please if you modify them, make sure they are updated in the original place
@author: joro
'''
import codecs
import numpy

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)



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
        a = numpy.rot90(listOfList)
        listOfList = numpy.flipud(a)
    
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



def getMeanAndStDevError(alignmentErrors):
    '''
    statistics for an array
    '''
        
    # convert to numpy array
    absalignmentErrors = [0] * len(alignmentErrors)
    for index, alError in enumerate(alignmentErrors):
        absalignmentErrors[index] = abs(alError)
    
    mean = numpy.round(numpy.mean(absalignmentErrors), decimals=2)
    median = numpy.round( numpy.median(absalignmentErrors), decimals=2)
    stDev = numpy.round( numpy.std(alignmentErrors), decimals=2)
    
    return mean, stDev, median