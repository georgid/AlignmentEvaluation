'''
Created on Oct 19, 2016

@author: joro
'''
from TextGrid_Parsing import TextGrid2WordList
import numpy


def eval_percentage_correct_phonemes(phoheme_list, mapB):
    '''
    Evaluate the percentage of correctly detected phoneme frames
    
    -generates a `mapB_oracle` matrix with same dim as `mapB`  with 1-s at correct phoneme and 0-s otherwise 
    -converts mapB to 1-s at  position of max prob 
    -intersects mapB_oracle and mapB column wise
    
    :param phoheme_list: list of phonemes as tuples  (  start_ts, end_ts, METU_phoneme)     
    :param mapB: ndarray with shape( len(num_phonemes_in_audio), len(num_observations)) 
    
    :returns:  
    percentage
     
    '''
    
    ######## generates a `mapB_oracle`  
    mapB_oracle = numpy.zeros(mapB.shape)
    
    
    ######## intersects mapB_oracle and mapB column wise
    

if __name__ == '__main__':
    
    annotationURI = 'example/02_Kimseye_2_zemin.TextGrid'
    tier = 0 # 'phonemes'
    
    annotationTokenListA = TextGrid2WordList(annotationURI, tier) 
#     load mapB
    mapB = []
    eval_percentage_correct_phonemes(annotationTokenListA, mapB )