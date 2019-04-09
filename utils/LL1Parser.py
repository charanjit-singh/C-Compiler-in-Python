"""
	Author: Charanjit Singh
	Website: https://charanjit-singh.github.io
	
	Description: This module Parses grammar using LL1 parsing Table.

"""
from utils.ParserUtils import *

class Entry():
	"""Entry"""
	def __init__(self, NonTerminal, Terminal, Rule = None): 
		self.non_terminal = NonTerminal
		self.terminal = Terminal
		self.rule = Rule

class LL1Parser():
	"""LL1Parser"""

	def __init__(self, grammar):
		self.grammar = grammar
		self.entries = []
		self.construct_parsing_table()

	def construct_parsing_table(self):
		for grammar_rule in self.grammar.grammar_rules:
			firsts = self.grammar.get_first_of_rule(grammar_rule)
			has_epsilon = False
			for first in firsts:
				if first.type == GrammarSymbol.TYPE_EPSILON:
					has_epsilon = True
					break
			if has_epsilon:
				# If Firsts contains EPSILON Entry, then add rule to follows (b)
				# Such that If A -> alpha then add A -> alpha to M[A,b]
				# If Follow in $ then add rule A -> alpha to M[A, $] { No need to check this condition. }
				follows = self.grammar.get_follows_for_lhs(grammar_rule.lhs).follows
				for follow in follows:
					self.add_entry(grammar_rule.lhs, follow, grammar_rule)
			else:
				for first in firsts:
					if first.type == GrammarSymbol.TYPE_EPSILON:
						continue
					self.add_entry(grammar_rule.lhs, first, grammar_rule)

	def add_entry(self, NonTerminal, Terminal, Rule):
		a = self.get_entry(NonTerminal, Terminal)
		if a:
			raise Exception("Not a LL1 Grammar")
		if not a:
			a = Entry(NonTerminal, Terminal, Rule)
			self.entries.append(a)
		a.rule = Rule


	def get_entry(self, NonTerminal, Terminal):
		for entry in self.entries:
			if entry.non_terminal.equals(NonTerminal) and entry.terminal.equals(Terminal):
				return entry 
		return None

	def print_parse_table(self):
		print("PARSE TABLE")
		for entry in self.entries:
			print(entry.non_terminal,' and ',entry.terminal, 'rule: ', entry.rule)
		print("---")

	def parse(self, stream):
		stack = []
		DOLLAR_SYMBOL = GrammarSymbol('$',GrammarSymbol.TYPE_DOLLAR)
		stack.append(DOLLAR_SYMBOL)
		# Initially push the $ grammar symbol to stack
		stream.append(DOLLAR_SYMBOL)
		stack.append(self.grammar.start_symbol)
		top_stack_symbol = stack[-1]
		ip = 0
		while not top_stack_symbol.equals(DOLLAR_SYMBOL):
			a = stream[ip]
			print('%38s | %5s'%(stack, a), end=" | ")
			if top_stack_symbol.equals(a):
				print("MATCH: %5s"%(a))
				stack.pop()
				ip += 1
			elif top_stack_symbol.type == GrammarSymbol.TYPE_TERMINAL:
				raise Exception("Failed to parse stream.")
			elif self.get_entry(top_stack_symbol, a) == None:
				raise Exception('Failed to parse stream.')
			elif self.get_entry(top_stack_symbol, a):
				production = self.get_entry(top_stack_symbol, a).rule
				stack.pop()
				print("RULE: ", production)
				if not production.rhs[0].equals(GrammarSymbol("EPSILON", GrammarSymbol.TYPE_EPSILON)):
					stack += reversed(production.rhs)
			top_stack_symbol = stack[-1]
			print('\n', end="")
		print("Parsed Successfully")

