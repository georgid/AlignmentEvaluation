'''
Created on Apr 3, 2014

@author: joro
'''
import sys
import subprocess
import os
import logging
from PraatVisualiser import openTextGridInPraat, PATH_TO_PRAAT

#used to open detected result only in TextGrid. after alignemnt algorithm is run.

parentDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__ ) ) )
PATH_TO_PRAAT_SCRIPT= os.path.join(parentDir, 'tab2TextGrid.rb')


PHRASE_ANNOTATION_EXT = '.TextGrid'
   
def doit(argv):    
    if len(argv) != 4  :
            print ("usage: {}  <pathToFiles>  <nameAudioFile> <extensionAligned>".format(argv[0]) )
            sys.exit();
    
    if not os.path.exists(PATH_TO_PRAAT):
        logging.warning("Praat not found at given path {}, skipping opening Praat ..\n")
        return
    
    comparisonTextGridURI =  os.path.join(sys.argv[1], sys.argv[2])  + PHRASE_ANNOTATION_EXT
    if os.path.isfile(comparisonTextGridURI):
        raw_input("there is already TextGrid with this file name! You may overwrite it!".format(comparisonTextGridURI))
        
    command = [PATH_TO_PRAAT, PATH_TO_PRAAT_SCRIPT, argv[1], argv[2], argv[3]]
    pipe = subprocess.Popen(command)
    pipe.wait()
        
    # open newly-created .TextGrid in  praat. OPTIONAL
    audio_URI = os.path.join(sys.argv[1], sys.argv[2])  + '.wav'
    openTextGridInPraat(sys.argv[1], sys.argv[2], audio_URI)
    
    
if __name__ == '__main__':
    doit(sys.argv)
    # example:
    #python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentEvaluation/tab2PraatAndOpenWithPRaat.py /Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik_short/1-05_Ruzgar_Soyluyor_Simdi_O_Yerlerde/ 1-05_Ruzgar_Soyluyor_Simdi_O_Yerlerde_2_zemin_from_16_459_to_38_756510 .wordsDurationSynthAligned
 