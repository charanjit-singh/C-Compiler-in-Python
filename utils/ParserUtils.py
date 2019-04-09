"""
	Author: Charanjit Singh
	Website: https://charanjit-singh.github.io

	Description: Parser Utility: It contains description of objects used in 'Parser'.

"""
import re

class Grammar():
	"""Context Free Grammar Rules"""

	def __init__(self):
		self.grammar_rules = []
		self.start_symbol = None
		self.get_rules_with_lhs = self.get_deltas

	def parse_from_file(self, grammar_file):
		grammerRules = []
		grammer_file_string = grammar_file.read().replace('\n',' ')
		grammer_rules = grammer_file_string.split(';')
		for grammer_rule in grammer_rules:
			producer = grammer_rule.split(':')[0].strip()
			if not len(producer):
				continue
			producer = GrammarSymbol(producer, GrammarSymbol.TYPE_NON_TERMINAL)
			if not self.start_symbol:
				# First Symbol is start symbol
				self.start_symbol = producer

			productions_this_producer = grammer_rule.split(':')[1].strip().split('|')

			for grammer_symbols in productions_this_producer:
				grammer_symbols = re.split('\s+', grammer_symbols.strip())
				grammerSymbols = []
				for grammer_symbol in grammer_symbols:
					symbol_type = ""
					# check if Terminal or NonTerminal by 
					# checking it's quotes or dualQuotes
					if grammer_symbol == "EPSILON":
						symbol_type = GrammarSymbol.TYPE_EPSILON
					elif re.match('[(\'.+\')|(\".+\"")]',grammer_symbol):
						symbol_type = GrammarSymbol.TYPE_TERMINAL
					else:
						symbol_type = GrammarSymbol.TYPE_NON_TERMINAL

					grammerSymbol = GrammarSymbol(grammer_symbol, symbol_type)
					grammerSymbols.append(grammerSymbol)

				grammerRule = GrammarRule(producer, grammerSymbols)
				grammerRules.append(grammerRule)

		self.grammar_rules = grammerRules
		return grammerRules

#  ---------------- LEFT FACTORING ----------------------------------

	def get_unique_lhs_s(self):
		unique_lhs_s = []
		for grammar_rule in self.grammar_rules:
			if not grammar_rule.lhs in unique_lhs_s:
				unique_lhs_s.append(grammar_rule.lhs)
		return unique_lhs_s

	def do_left_factoring(self):
		while True:
			restart_loop = False
			unique_lhs_s = self.get_unique_lhs_s()
			for unique_lhs in unique_lhs_s:
				deltas = self.get_deltas(unique_lhs)
				# deltas  = Production with this lhs
				alphas = []
				gammas = []
				for delta in deltas:
					for inner_delta in deltas:
						if delta == inner_delta:
							continue
						if delta.rhs[0].content == inner_delta.rhs[0].content:
							alphas.append(delta)

				for delta in deltas:
					if not delta in alphas:
						gammas.append(delta) 

				if len(alphas)>0:
					a_prime = GrammarSymbol(self.get_unique_new_name(unique_lhs.content), GrammarSymbol.TYPE_NON_TERMINAL)
					alpha_symbol = alphas[0].rhs[0]
					self.remove_all_rules_with_lhs(unique_lhs)
					# Remove all rules with rule unique_lhs
					a_alpha_a_prime_rule = GrammarRule( unique_lhs ,[alpha_symbol, a_prime] )
					self.grammar_rules.append(a_alpha_a_prime_rule)

					for gamma in gammas:
						gamma_rule = GrammarRule(gamma.lhs, gamma.rhs)
						self.grammar_rules.append(gamma_rule)

					for alpha in alphas:
						beta_rhs = alpha.rhs[1:]
						if len(beta_rhs) == 0:
							beta_rhs = [ GrammarSymbol("EPSILON", GrammarSymbol.TYPE_EPSILON)]
						beta_rule = GrammarRule(a_prime, beta_rhs)
						self.grammar_rules.append(beta_rule)
					restart_loop = True

			if not restart_loop:
				break

		return self.grammar_rules

# ------------------- END LEFT FACTORING -----------------------------

# ------------------ LEFT RECURSION REMOVAL --------------------------

	def remove_all_rules_with_lhs(self, lhs):
		temp_grammar_rules = []
		for grammar_rule in self.grammar_rules:
			if not grammar_rule.lhs == lhs:
				temp_grammar_rules.append(grammar_rule)
		self.grammar_rules = temp_grammar_rules
		return self.grammar_rules

	def get_unique_new_name(self, lhs):
		"""Returns Unique New Name"""
		name = lhs.content + "_prime"
		while True:
			restart_loop = False
			for grammar_rule in self.grammar_rules:
				if grammar_rule.lhs.content == name:
					name += "_prime"
					restart_loop = True
			if not restart_loop:
				break
		return name
	def update_left_recursive_grammar(self, **kwargs):
		recursive_grammer_rule = kwargs['recursive_grammer_rule']
		beta = kwargs['beta']
		alpha = kwargs['alpha']
		grammerRules = self.grammar_rules
		lhs = recursive_grammer_rule.lhs
		lhs_prime = GrammarSymbol(self.get_unique_new_name(lhs), GrammarSymbol.TYPE_NON_TERMINAL)
		alpha.append(lhs_prime)
		# Generate A_prime
		EPSILON_SYMBOL = GrammarSymbol("EPSILON", GrammarSymbol.TYPE_EPSILON)
		prime_grammar_rule = GrammarRule(lhs_prime, alpha)
		self.grammar_rules.append(prime_grammar_rule)
		prime_grammar_rule = GrammarRule(lhs_prime, [EPSILON_SYMBOL,])
		self.grammar_rules.append(prime_grammar_rule)
		self.grammar_rules = self.remove_all_rules_with_lhs(lhs)

		# If there is no beta then 
		if len(beta) == 0:
			beta_lhs = lhs
			beta_rhs = [] 
			beta_rhs.append(lhs_prime)
			beta_grammar_rule = GrammarRule(beta_lhs, beta_rhs)
			self.grammar_rules.append(beta_grammar_rule)

		# for all beta's generate [ beta, a_prime ] production and create  
		for grammar_rule in beta:
			beta_lhs = lhs
			beta_rhs = grammar_rule.rhs
			beta_rhs.append(lhs_prime)
			beta_grammar_rule = GrammarRule(beta_lhs, beta_rhs)
			self.grammar_rules.append(beta_grammar_rule)

		return self.grammar_rules



	def get_betas_for_recursion_removal(self, lhs, _grammar_rule):
		beta = []
		for grammar_rule in self.grammar_rules:
			if grammar_rule.lhs.content == lhs.content and not (grammar_rule == _grammar_rule):
				beta.append(grammar_rule)
		return beta

	def remove_left_recursion(self):
		while True:
			restart_loop = False
			for grammar_rule in self.grammar_rules:
				lhs = grammar_rule.lhs
				rhs = grammar_rule.rhs
				IstSymbol = grammar_rule.get_rhs_first_symbol()
				if IstSymbol.type == GrammarSymbol.TYPE_NON_TERMINAL:
					if lhs.content == IstSymbol.content:
						alpha = rhs[1:]
						beta = self.get_betas_for_recursion_removal(lhs, grammar_rule)
						self.grammar_rules = self.update_left_recursive_grammar(
												alpha = alpha,
												beta = beta,
												recursive_grammer_rule = grammar_rule
											)
						restart_loop = True
						break
			if not restart_loop:
				break

		return self.grammar_rules

	def get_deltas(self, lhs):
		deltas = []
		for grammar_rule in self.grammar_rules:
			if grammar_rule.lhs.content == lhs.content:
				deltas.append(grammar_rule)
		return deltas

	def remove_rule(self, rule):
		rules = []
		for grammar_rule in self.grammar_rules:
			if not rule == grammar_rule:
				rules.append(grammar_rule)
		self.grammar_rules = rules
		return self.grammar_rules

	def expand_Aj_to_Ai(self, Aj, Ai):
		deltas = self.get_deltas(Aj.lhs)
		gamma = Ai.rhs[1:]
		# get all Ai s

		self.grammar_rules = self.remove_rule(Ai)
		self.print_grammar()
		for delta in deltas:
			new_grammar_symbols = delta.rhs + gamma
			if len(new_grammar_symbols) == 0:
				new_grammar_symbols = [ GrammarSymbol("EPSILON", GrammarSymbol.TYPE_EPSILON), ]
			new_grammar_rule = GrammarRule(Ai.lhs, new_grammar_symbols)
			self.grammar_rules.append(new_grammar_rule)
		return self.grammar_rules


	def is_production_from_Ai_to_Aj(self, Ai, Aj):
		""" For Indirect Left Recursion Removal. """
		for grammar_rule in self.grammar_rules:
			if grammar_rule.lhs == Ai.lhs:
				if grammar_rule.rhs[0].content == Aj.lhs.content and grammar_rule.rhs[0].type == GrammarSymbol.TYPE_NON_TERMINAL:
					if grammar_rule == Ai:
						# TODO: Check Self Loop
						return True
					return False
		return False

	def remove_indirect_left_recursion(self):
		# impose an order on Grammar Rules
		i = 0 
		self.remove_left_recursion()
		
		while True:
			restart_loop = False
			for grammar_rule in self.grammar_rules:
				grammar_rule.order = i
				i += 1

			for i in range(len(self.grammar_rules)):
				for j in range(i):
					if self.is_production_from_Ai_to_Aj(self.grammar_rules[i], self.grammar_rules[j]):
						self.expand_Aj_to_Ai(self.grammar_rules[j], self.grammar_rules[i])
						self.remove_left_recursion()
						restart_loop = True
						break
				if restart_loop:
					break
			if not restart_loop:
				break
		

# ------------------ END LEFT RECURSION REMOVAL ---------------------------------

# --------------------------- GET FIRSTS ----------------------------------------

	def get_recursively_firsts(self,index, rhs, lhs):
		firsts = []
		try:
			symbol = rhs[index]
		except IndexError:
			# index - 1 = Last terminal
			if rhs[index-1].type == GrammarSymbol.TYPE_EPSILON:
				return [rhs[index-1]]

			if rhs[index-1].type == GrammarSymbol.TYPE_NON_TERMINAL:
				return self.get_first_of_lhs(rhs[index-1])

			return []
		if symbol.type == GrammarSymbol.TYPE_TERMINAL:
			return [symbol]
		
		if symbol.type == GrammarSymbol.TYPE_EPSILON:
			firsts = self.get_recursively_firsts( index + 1, rhs, lhs)
			return firsts

		temp_firsts = self.get_first_of_lhs(symbol)
		for temp_first in temp_firsts:
			if temp_first.type == GrammarSymbol.TYPE_TERMINAL:
				firsts.append(temp_first)
			elif temp_first.type == GrammarSymbol.TYPE_EPSILON:
				firsts += self.get_recursively_firsts( index + 1, rhs, lhs)
		# remove duplicates
		temp_firsts = []
		for first in firsts:
			if not first in temp_firsts:
				temp_firsts.append(first)
		return temp_firsts
	
	def get_first_of_lhs(self, lhs):
		firsts = []
		deltas = self.get_deltas(lhs)
		for delta in deltas:
			IstSymbol = delta.rhs[0]
			if IstSymbol.type == GrammarSymbol.TYPE_TERMINAL:
				firsts.append(IstSymbol)
			else:
				firsts += self.get_recursively_firsts(0, delta.rhs, lhs)
		return firsts

	def get_first_of_rule(self, delta):
		# Delta = Rule
		firsts = []
		IstSymbol = delta.rhs[0]
		if IstSymbol.type == GrammarSymbol.TYPE_TERMINAL:
			firsts.append(IstSymbol)
		else:
			firsts += self.get_recursively_firsts(0, delta.rhs, delta.lhs)
		return firsts

	def get_firsts(self):
		unique_lhs_s = self.get_unique_lhs_s()
		firsts = []
		for unique_lhs in unique_lhs_s:
			firsts.append({'lhs': unique_lhs, 'firsts' : self.get_first_of_lhs(unique_lhs)})
		return firsts
			

# ---------------------------- END FIRSTS -----------------------------------------
# --------------------------- FIND FOLLOWS ----------------------------------------

	def get_follows_for_lhs(self, lhs):
		follows = self.get_follows()
		for follow in follows:
			if follow.symbol.equals(lhs):
				return follow
		return None

	def get_follows(self):
		unique_lhs_s = self.get_unique_lhs_s()
		follows = []
		class Follow():
			"""Follow Object"""
			def __init__(self, symbol):
				self.symbol = symbol
				self.follows = set()

		def get_follow(s):
			for follow in follows:
				if follow.symbol.content == s.content:
					return follow
			return None	

		def are_equal(d, s):
			d_array  = [i.content for i in list(d)]
			s_array = [i.content for i in list(s)]
			print(d_array, s_array)
			for d in d_array:
				if not d in s_array:
					return False

			for s in s_array:
				if not s in d_array:
					return False

			return True

		for unique_lhs in unique_lhs_s:
			follow = Follow(unique_lhs)
			if self.start_symbol == unique_lhs:
				follow.follows = follow.follows.union({GrammarSymbol("$", GrammarSymbol.TYPE_DOLLAR)})
			follows.append(follow)
			# Initialise with phi.

		for k in range(200):
			for grammar_rule in self.grammar_rules:
				trailer = get_follow(grammar_rule.lhs).follows
				betas = grammar_rule.rhs
				index = 0
				for beta in reversed(betas):
					if beta.type == GrammarSymbol.TYPE_NON_TERMINAL:
						
						get_follow(beta).follows = get_follow(beta).follows.union(trailer) 
						firsts = self.get_first_of_lhs(beta)
						contains_epsilon = False
						for first in firsts:
							if first.type == GrammarSymbol.TYPE_EPSILON:
								contains_epsilon = True
								break
						if contains_epsilon:
							first_without_epsilon = []
							for first in firsts:
								if not first.type == GrammarSymbol.TYPE_EPSILON:
									first_without_epsilon.append(first)
							trailer = trailer.union(set(first_without_epsilon))
						else:
							trailer = set(firsts)
					else:
						trailer = set(self.get_recursively_firsts(len(grammar_rule.rhs) - index - 1, grammar_rule.rhs , grammar_rule.lhs))

					index += 1

		for follow in follows:
			# REMOVE DUPLICATES
			temp_f = []
			for f in follow.follows:
				if not f.content in [ i.content for i in temp_f]:
					temp_f.append(f)
			follow.follows = temp_f

		return follows
			
# --------------------------- END FOLLOWS ----------------------------------------
	def print_grammar(self):
		print('Grammar: -------------------------------------')
		print("Start Symbol: [ ", self.start_symbol.content, ' ] ')
		for grammar_rule in self.grammar_rules:
			print(grammar_rule.lhs.content, end="-> ")
			for grammar_symbol in grammar_rule.rhs:
				print(grammar_symbol.content, end=" ")
			print('\n')
		print('-----------------------------------------------')

	def get_terminals(self):
		terminals = []
		for grammar_rule in self.grammar_rules:
			if grammar_rule.type == GrammarSymbol.TYPE_TERMINAL:
				terminals.append(grammar_rule)
		return terminals

	def get_non_terminals(self):
		non_terminals = []
		for grammar_rule in self.grammar_rules:
			if grammar_rule.lhs.type == GrammarSymbol.TYPE_NON_TERMINAL:
				non_terminals.append(grammar_rule.lhs)
		return non_terminals

	def get_all_grammar_symbols(self):
		grammar_symbols = self.get_non_terminals()
		return grammar_symbols

class GrammarRule():
	"""
		Production Rule for grammar.
			lhs: GrammarSymbol
			rhs: Array<GrammarSymbol>
	"""
	def __init__(self, lhs, rhs):
		self.lhs = lhs
		self.rhs = rhs
		self.order = 0 # for indirect left-recursion removal

	def get_rhs_first_symbol(self):
		"""Returns Ist Grammer Symbol"""
		return self.rhs[0]

	def equals(self, rule):
		""" Checks if two rules are same."""
		if self.lhs.equals(rule.lhs):
			if len(self.rhs) == len(rule.rhs):
				i = 0
				for rhs_symbol in self.rhs:
					if not rhs_symbol.equals(rule.rhs[i]):
						return False
					i += 1
				return True
			else:
				return False
		return False

	def __repr__(self):
		temp_str = ""
		for x in self.rhs:
			temp_str += x.content + ' '
		return "<%s : %s >"%(self.lhs.content, temp_str)
		
class GrammarSymbol():
	"""Grammar Symbol."""
	TYPE_EPSILON = 0
	TYPE_NON_TERMINAL = 1
	TYPE_TERMINAL = 2
	TYPE_DOLLAR = 3

	def __init__(self, content, _type):
		self.content = content
		self.type = _type

	def __repr__(self):
		return '<' + self.content + '>'

	def equals(self, other):
		return self.content == other.content and self.type == other.type
		