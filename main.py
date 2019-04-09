"""
	Author: Charanjit Singh
	Website: https://charanjit-singh.github.io

	Description: 'C' Compiler written in Python3.
	Module Description: This is driver module, that binds and drives other modules in a sequential manner.

"""

from lexical_analyser import *
from parser import *

def main():
	input_file_path = 'input.c'
	grammar_file_path = 'assets/grammar.gra'
	input_program_file = open(input_file_path,'r')
	input_grammar_file = open(grammar_file_path,'r')
	lexical_analyser = LexicalAnalyser( input_file = input_program_file )
	# lexical_analyser.analyse()  
	parser = Parser( input_file = input_grammar_file )

if __name__ == '__main__':
	main()