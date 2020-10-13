#authors Georgi Dzhambazov, Chitralekha Gupta

import os
import glob
import pdb
import sys
from compute_wer_script import ComputeWER

project_dir = os.path.join(os.path.dirname(__file__), '..')
if project_dir not in sys.path:
    sys.path.append(project_dir)
    
from align_eval.Utilz import writeCsv

EXTENSION_RECO = '.transcribed.txt'


def MakeAptFile(outfile,infile,filename):
    fout = open(outfile,'w')
    line = open(infile,'r').readlines()
    if len(line)>1: print("Please check")
    fout.write(filename+' '+line[0].lower())
    fout.close()


def main_eval_all_files(argv):
    
    if len(argv) != 4:
        sys.exit('usage: {} <path dir with to reference word boundaries> <path to dir with detected word boundaries> <path_output>'.format(sys.argv[0]))
    refs_dir_URI = argv[1]
    detected_dir_URI = argv[2]
    a = os.path.join(detected_dir_URI, "*{}".format(EXTENSION_RECO))
    lab_files = glob.glob(a)
    print('Found {}  files'.format(len(lab_files)))


    results = [['Track,WER,Insertions,Deletions,Substitutions,TotalWords']]
    for lab_file in lab_files:
        base_name = os.path.basename(lab_file)
        extension_length = len(EXTENSION_RECO)
        ref_file = os.path.join(refs_dir_URI, base_name[:-extension_length] + '.words.txt')
        MakeAptFile('ref', ref_file, base_name[:-extension_length])
        MakeAptFile('transcr', lab_file, base_name[:-extension_length])
        WER,ins,dele,sub,total = ComputeWER('ref','transcr')
        print("WER = ",WER)
        print("ins,del,sub,totalwords = ",ins,dele,sub,total)
        results.append([base_name[:-extension_length], '{:.3f}'.format(float(WER)),
                        '{}'.format(int(ins)),
                         '{}'.format(int(dele)),
                        '{}'.format(int(sub)),
                        '{}'.format(int(total))])
    output_URI = argv[3]
    writeCsv(os.path.join(output_URI, 'results.csv'), results)

if __name__ == '__main__':
#     main_eval_one_file(sys.argv)
    main_eval_all_files(sys.argv)