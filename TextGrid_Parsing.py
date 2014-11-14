#! /usr/bin/python
# -*- coding: utf-8 -*-
import textgrid as tgp
import sys, os

from setuptools.command.easy_install import sys_executable
sys.path.append(os.path.realpath('../Batch_Processing/'))
# import Batch_Proc_Essentia as BP  # @UnresolvedImport


      

tier_names = ["phonemes", 'words', "phrases" ];

'''
textGrid to dictionary column file 
'''
def TextGrid2Dict(textgrid_file, outputFileName):
	
	par_obj = tgp.TextGrid.load(textgrid_file)	#loading the object	
	tiers= tgp.TextGrid._find_tiers(par_obj)	#finding existing tiers
		
	outputFileHandle = open(outputFileName, 'w')
	
	
	for tier in tiers:
		
		if tier.tier_name() == tier_names[2]:	#iterating over tiers and selecting the one specified
			
			tier_details = tier.make_simple_transcript();		#this function parse the file nicely and return cool tuples
			
			for line in tier_details:
				
				outputFileHandle.write(line[0] + "\t" + line[2]+ "\n") 

	outputFileHandle.close()		

'''
parse textGrid into a python list of tokens 
@param whichLevel : 0 -  phonemes,   2 - phrases
TODO: implement: 1- words  
'''	
def TextGrid2WordList(textgrid_file, whichLevel=2):
		
		beginTsAndWordList=[]
		
		par_obj = tgp.TextGrid.load(textgrid_file)	#loading the object	
		tiers= tgp.TextGrid._find_tiers(par_obj)	#finding existing tiers		
		
		isTierFound = 0
		for tier in tiers:
		
			if tier.tier_name() == tier_names[int(whichLevel)]:	#iterating over tiers and selecting the one specified
				isTierFound = 1
				tier_details = tier.make_simple_transcript();		#this function parse the file nicely and return cool tuples
				
				for line in tier_details:
					beginTsAndWordList.append([line[0], line[1], line[2]])
		
		if not isTierFound:
			sys.exit('tier in file {0} might not be named correctly. Name it {1}' .format(textgrid_file, tier_names[whichLevel]))
		return beginTsAndWordList		


##################################################################################



if __name__ == '__main__':
	
	TextGrid2Dict(sys.argv[1], sys.argv[2])
