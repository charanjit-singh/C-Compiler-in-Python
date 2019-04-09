"""
	Author: Charanjit Singh
	Website: https://charanjit-singh.github.io
	
	Description: This module parses the given 'program file' using "Context Free Grammar" and generates
				 the syntax Tree from input Token Stream.

"""

from utils.ParserUtils import *
from utils.LL1Parser import *
from utils.SLRParser import *

class Parser():

	def __init__(self, **kwargs):
		self.grammar_file = kwargs.get('input_file', None)
		self.grammar = Grammar()
		self.grammar.parse_from_file(self.grammar_file)
		print("Original",end=" ")
		self.grammar.print_grammar()
		self.grammar.remove_indirect_left_recursion()
		self.grammar.do_left_factoring()
		firsts = self.grammar.get_firsts()
		follows = self.grammar.get_follows()
		print("FIRSTS")
		for first in firsts:
			print('  >>> ',first['lhs'] ,':',first['firsts'])

		print("FOLLOWS")
		for follow in follows:
			print('  >>> ',follow.symbol ,':',list(follow.follows))
		parser = LL1Parser(self.grammar)
		stream = []
		stream.append(GrammarSymbol("'a'", GrammarSymbol.TYPE_TERMINAL))
		stream.append(GrammarSymbol("'b'", GrammarSymbol.TYPE_TERMINAL))
		stream.append(GrammarSymbol("'a'", GrammarSymbol.TYPE_TERMINAL))
		# stream.append(GrammarSymbol("'id'", GrammarSymbol.TYPE_TERMINAL))
		# stream.append(GrammarSymbol("'*'", GrammarSymbol.TYPE_TERMINAL))
		# stream.append(GrammarSymbol("'id'", GrammarSymbol.TYPE_TERMINAL))
		try:
			parser.parse(stream)
		except Exception as e:
			print("\nError: ",str(e))
		# Parser = SLRParser(self.grammar)
		# self.grammar.print_grammar()

		

