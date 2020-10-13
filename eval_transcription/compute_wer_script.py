import os
import subprocess
import sys


def ComputeWER(ref,hyp):
        command = 'compute-wer --text --mode=all ark:'+ref+' ark:'+hyp
        proc = subprocess.Popen(command,stdout=subprocess.PIPE,shell=True)
        (out,err) = proc.communicate()
        out = str(out)
        #output format: b'%WER 16.67 [ 2 / 12, 0 ins, 0 del, 2 sub ]\n%SER 100.00 [ 1 / 1 ]\nScored 1 sentences, 0 not present in hyp.\n'
        WER = out.split(' ')[1] #WER = 100*(insertions+deletions+substitutions)/totalwords
        ins = out.split('ins')[0].split(' ')[-2] #insertions
        dele = out.split('del')[0].split(' ')[-2] #deletions
        sub = out.split('sub')[0].split(' ')[-2] #substitutions
        total = out.split('/')[1].split(' ')[1].replace(',','') #total number of words
        return WER,ins,dele,sub,total

if __name__=='__main__':
	reffile = sys.argv[1]
	hypfile = sys.argv[2]
	WER,ins,dele,sub,total = ComputeWER(reffile,hypfile)
	print("WER = ",WER)
	print("ins,del,sub,totalwords = ",ins,dele,sub,total)


