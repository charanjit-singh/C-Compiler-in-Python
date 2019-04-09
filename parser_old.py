import re


class GrammerSymbol(object):
	"""
		Grammer Symbol:
			content: string | None ( in case of EPSILON )
			type : "Terminal" | "NonTerminal" | "EPSILON"
	"""
	def __init__(self, content, type_):
		self.content = content
		self.type = type_

	def __str__(self):
		return " %s [%s]"%(self.content, self.type)		

	def __repr__(self):
		return self.__str__()		


class Production():
	"""
		Production is an array of grammer_symbols
	"""
	def __init__(self, grammer_symbols = []):
		self.grammer_symbols = grammer_symbols
		self.get_gamma = self.get_alpha

	def __str__(self):
		grammerSymbolsString = ""
		for grammer_symbol in self.grammer_symbols:
			grammerSymbolsString += str(grammer_symbol) + ' ' 

		return grammerSymbolsString

	def __repr__(self):
		return self.__str__()

	def get_alpha(self):
		if not len(self.grammer_symbols)>1:
			raise Exception("Cannot generate Alpha")
		return self.grammer_symbols[1:]

	def get_all_but_first(self):
		if not len(self.grammer_symbols)>1:
			raise Exception("Cannot generate Alpha")
		return self.grammer_symbols[1:]

	def get_first_symbol(self):
		return self.grammer_symbols[0]

	def get_symbol_at(self, index):
		return self.grammer_symbols[index]


class GrammerRule():
	"""
		Grammer Rule:
			Producer : string
			Production : [ grammer_symbol, grammer_symbol, ... ]
					      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^----Production
	"""

	def __init__(self, producer, production):
		self.producer = producer
		self.production = production
		self.id = None

	def __str__(self):
		return "\n%s :->  %s"%(self.producer, self.production)		
	
	def __repr__(self):
		return self.__str__()

	def getProductionSymbols(self):
		string = ""
		for i in self.production.grammer_symbols:
			string += i.content + ' '
		return string


def getBetaOf(producer, current_production, grammerRules):
	beta = []
	for grammer_rule in grammerRules:
		if grammer_rule.producer == producer and not grammer_rule.production == current_production:
			beta.append(grammer_rule)
	return beta

def getDeltas(producer, grammerRules):
	deltas = []
	for grammer_rule in grammerRules:
		if grammer_rule.producer == producer:
			deltas.append(grammer_rule)
	return deltas

def expandAjtoAi(Aj, Ai, grammerRules):
	deltas = getDeltas(Aj.producer, grammerRules)
	print('Ai=', Ai, '\nAj= ', Aj, "\ngrammerRules:")
	gamma = Ai.production.get_gamma()
	# remove Ai -> Ajγ
	print("gamma for ",Ai,":", gamma)
	print("deltas for ", Aj, ":", deltas)
	grammerRules = removeAllRulesWithProducer(Ai.producer, grammerRules)
	# then replace Ai→Ajγ with a set of productions Ai→δ1γ |δ2γ |···|δkγ.
	for delta in deltas:
		new_grammer_symbols = delta.production.grammer_symbols + gamma
		new_production = Production(new_grammer_symbols)
		new_grammer_rule = GrammerRule(Ai.producer, new_production)
		grammerRules.append(new_grammer_rule)

	return grammerRules


def removeAllRulesWithProducer(producer, grammerRules):
	tempGrammerRules = []
	for grammer_rule in grammerRules:
		if not grammer_rule.producer == producer:
			tempGrammerRules.append(grammer_rule)
	return tempGrammerRules 

def updateLeftRecursiveGrammer(**kwargs):
	recursive_grammer_rule = kwargs['recursive_grammer_rule']
	beta = kwargs['beta']
	alpha = kwargs['alpha']
	grammerRules = kwargs['grammerRules']
	producer = recursive_grammer_rule.producer

	# generate a_prime
	producer_a_prime = producer + "_prime"
	grammer_symbol_a_prime = GrammerSymbol(producer_a_prime, "NonTerminal")
	# alpha, a_prime
	alpha.append(grammer_symbol_a_prime)
	production_a_prime = Production(alpha)
	# EPSILON
	EPSILON_SYMBOL = GrammerSymbol("EPSILON", "EPSILON")
	production_epsilon = Production([EPSILON_SYMBOL,])
	""" 
		create two new grammer rules:
			producer_a_prime :-> production_a_prime
			producer_a_prime :-> {EPSILON}
	"""
	prime_grammer_rule = GrammerRule(producer_a_prime, production_a_prime)
	prime_epsilon_grammer_rule = GrammerRule(producer_a_prime, production_epsilon)
	grammerRules.append(prime_grammer_rule)
	grammerRules.append(prime_epsilon_grammer_rule)


	# remove all productions with producer: producer
	grammerRules = removeAllRulesWithProducer(producer, grammerRules)

	# for all beta's generate [ beta, a_prime ] production and create  
	for grammer_rule in beta:
		beta_producer = producer # i.e. 'a' itself
		beta_production = grammer_rule.production
		beta_production.grammer_symbols.append(grammer_symbol_a_prime)
		beta_grammer_rule = GrammerRule(beta_producer, beta_production)
		grammerRules.append(beta_grammer_rule)
	
	return grammerRules


def removeLeftRecursion(grammerRules):
	recursive_at = []
	while(1):
		restart_loop = False
		for grammer_rule in grammerRules:
			producer = grammer_rule.producer
			production = grammer_rule.production
			Ist_symbol = production.get_first_symbol()

			if Ist_symbol.type == "NonTerminal":
				if producer == Ist_symbol.content:
					recursive_at.append(producer)
					# now remove left recursion and regenerate the rules
					# get_alpha
					alpha = production.get_alpha()
					# get beta
					beta = getBetaOf(producer, production, grammerRules )
					grammerRules = updateLeftRecursiveGrammer(
							alpha = alpha,
							beta = beta,
							recursive_grammer_rule = grammer_rule,
							grammerRules = grammerRules
						)
					restart_loop = True
					# restart again this loop
					break

		if not restart_loop:
			break

	return {"recursive_at": recursive_at, "grammerRules": grammerRules}

def isProductionFromAiToAj(Ai, Aj, grammerRules):
	for grammer_rule in grammerRules:
		if grammer_rule.producer == Ai.producer:
			if grammer_rule.production.get_first_symbol().content == Aj.producer and grammer_rule.production.get_first_symbol().type == "NonTerminal":
				print("YES", Aj.producer, " and ", Ai.producer )
				return True 
	return False

def removeIndirectLeftRecursion(grammerRules):
	# TODO: Complete this function
	grammerRules = removeLeftRecursion(grammerRules)['grammerRules']

	# impose Order on grammer Rules
	i = 0
	for grammer_rule in grammerRules:
		grammer_rule.id = i
		i += 1

	while 1:
		restart_loop = False
		for i in range(len(grammerRules)):
			new_grammerRules = grammerRules
			for j in range(i):
				if isProductionFromAiToAj( grammerRules[i] , grammerRules[j], grammerRules):
					new_grammerRules = expandAjtoAi(grammerRules[i], grammerRules[j], new_grammerRules)
					restart_loop = True
			grammerRules = removeLeftRecursion(new_grammerRules)['grammerRules']
			if restart_loop:
				break
		if not restart_loop:
			break
	print(grammerRules)
	return grammerRules

def getAllProducers(grammerRules):
	unique_producers = []
	for grammer_rule in grammerRules:
		if not grammer_rule.producer in unique_producers:
			unique_producers.append(grammer_rule.producer)

	return unique_producers

def getRecusivelyFirsts( index, production, grammerRules):
	firsts = []
	try:
		symbol =  production.get_symbol_at(index)
	except IndexError:
		return []
	if symbol.type=="Terminal":
		return [symbol]
	tempFirsts = getFirstOfProducer(symbol.content, grammerRules)	
	for temp_first in tempFirsts:
		if temp_first.type == "Terminal":
			firsts.append(temp_first)
		elif temp_first.type == "EPSILON":
			firsts += getRecusivelyFirsts( index + 1, production, grammerRules)
	return firsts

def getFirstOfProducer(producer, grammerRules):
	firsts = []
	deltas = getDeltas(producer, grammerRules)
	for delta in deltas:
		Ist_symbol = delta.production.get_first_symbol()
		if Ist_symbol.type == "Terminal" or Ist_symbol.type == "EPSILON":
			firsts.append(Ist_symbol)
		elif Ist_symbol.type == "NonTerminal":
			firsts += getRecusivelyFirsts( 0, delta.production, grammerRules)
	return firsts

def getFirst(grammerRules):
	producers = getAllProducers(grammerRules)
	firsts = []
	for producer in producers:
		firsts.append({'producer':producer, 'firsts': getFirstOfProducer(producer, grammerRules)})
	return firsts

def getRecusivelyFollows(index, starting, production, grammerRules, last=False):
	firsts = []
	is_starting = starting == production

	try:
		symbol =  production.get_symbol_at(index)
	except IndexError:
		if is_starting:
			return['$']
		return []

	if symbol.type=="Terminal":
		return [symbol]

	tempFirsts = getFirstOfProducer(symbol.content, grammerRules)	
	i = 0
	print("tempFirsts:",tempFirsts)
	for temp_first in tempFirsts:
		i += 1
		if temp_first.type == "Terminal":
			firsts.append(temp_first)
		elif temp_first.type == "EPSILON":
			firsts += getRecusivelyFollows( index + 1, starting, production, grammerRules, last)
	return firsts


def getProductionsWhoseRightSideContains(producer, grammerRules):
	grammer_rules = []
	for grammer_rule in grammerRules:
		index = 0
		for grammer_symbol in grammer_rule.production.grammer_symbols:
			if grammer_symbol.type == "NonTerminal" and grammer_symbol.content == producer:
				grammer_rules.append({"grammer_rule": grammer_rule, "index": index})
			index = index + 1

	return grammer_rules

def getFollowOfProducer(producer,  starting, grammerRules):
	follows = []
	is_starting = False

	if producer == starting:
		is_starting = True
	if is_starting:
		follows.append('$')
	RHS_production_rules = getProductionsWhoseRightSideContains(producer, grammerRules)
	print("RHS_production_rules:",RHS_production_rules)
	for grammer_rule in RHS_production_rules:
		is_last = False
		if grammer_rule['index'] == len(grammer_rule['grammer_rule'].production.grammer_symbols):
			is_last = True
		follows += getRecusivelyFollows(grammer_rule['index'] + 1 , starting, grammer_rule['grammer_rule'].production, grammerRules, is_last)

	return follows

def getFollow(grammerRules):
	producers = getAllProducers(grammerRules)
	starting = producers[0]

	follows = []
	for producer in producers:
		follows.append({'producer':producer, 'follows': getFollowOfProducer(producer, starting, grammerRules)})

	return follows

def getGrammerRulesFromFile(file):
	grammerRules = []
	grammer_file_string = file.read().replace('\n',' ')
	grammer_rules = grammer_file_string.split(';')
	for grammer_rule in grammer_rules:
		producer = grammer_rule.split(':')[0].strip()
		if not len(producer):
			continue

		productions_this_producer = grammer_rule.split(':')[1].strip().split('|')
		for grammer_symbols in productions_this_producer:
			grammer_symbols = re.split('\s+', grammer_symbols.strip())
			grammerSymbols = []
			for grammer_symbol in grammer_symbols:
				symbol_type = ""
				# check if Terminal or NonTerminal by 
				# checking it's quotes or dualQuotes
				if grammer_symbol == "EPSILON":
					symbol_type = "EPSILON"
				elif re.match('[(\'.+\')|(\".+\"")]',grammer_symbol):
					symbol_type = "Terminal"
				else:
					symbol_type = "NonTerminal"

				grammerSymbol = GrammerSymbol(grammer_symbol, symbol_type)
				grammerSymbols.append(grammerSymbol)
			production = Production(grammerSymbols)
			grammerRule = GrammerRule(producer, production)
			grammerRules.append(grammerRule)
	return grammerRules

def getAlphaGammaForLeftFactoring(producer, deltas, grammerRules):
	alphas = []
	gammas = []
	for delta in deltas:
		for inner_delta  in deltas:
			if inner_delta == delta:
				continue
			if delta.production.get_first_symbol().content == inner_delta.production.get_first_symbol().content:
				alphas.append(delta.production)
				
	print("alphas",alphas)

	for delta in deltas:
		if not delta.production in alphas:
			gammas.append(delta.production)

	return {'alphas': alphas, 'gammas': gammas}

def doLeftFactoring(grammerRules):
	while(1):
		restart_loop = False
		producers = getAllProducers(grammerRules)
		for producer in producers:
			deltas = getDeltas(producer, grammerRules)
			print("producer", producer)
			alphas_gammas = getAlphaGammaForLeftFactoring(producer, deltas, grammerRules)
			if len(alphas_gammas['alphas']):
				# remove left factoring
				betas = []
				gammas = alphas_gammas['gammas']
				alpha_symbol = alphas_gammas['alphas'][0].get_first_symbol()
				for beta in alphas_gammas['alphas']:
					betas.append(beta.get_all_but_first())
				print("There is left Factoring at", alpha_symbol)
				print("betas: ", betas)
				print("gammas: ", gammas)
				grammerRules = removeAllRulesWithProducer(producer, grammerRules)
				new_producer = producer + '_prime'

				for beta in betas:
					
					new_grammer_symbols = Production(beta)
					new_grammer_rule = GrammerRule(new_producer, new_grammer_symbols)
					grammerRules.append(new_grammer_rule)
					
				new_grammer_symbols = Production(gammas)
				new_grammer_rule = GrammerRule(producer, new_grammer_symbols)
				grammerRules.append(new_grammer_rule)

				new_grammer_symbols = [ alpha_symbol , GrammerSymbol(new_producer, "NonTerminal") ]

				new_grammer_rule = GrammerRule(producer, new_grammer_symbols)
				grammerRules.append(new_grammer_rule)

				restart_loop = True
		if not restart_loop:
			break

	print(grammerRules)
	return grammerRules

def writeGrammerToFile(grammerRules, file):
	for grammer_rule in grammerRules:
		file.write("%s : %s;\n"%(grammer_rule.producer, grammer_rule.getProductionSymbols()))
	return

def writeSummaryToFile(firsts, follows, file):
	file.write("\tFIRSTs\n\n")
	for first in firsts:
		first_string = ""
		for first_symbol in first['firsts']:
			first_string += first_symbol.content + ' '
		file.write("%s : { %s }\n"%( first['producer'], first_string))


	file.write("\nFOLLOWs\n\n")
	for follow in follows:
		follow_string = ""
		for follow_symbol in follow['follows']:
			if type(follow_symbol) == str:
				follow_string += follow_symbol + ' '
			else:
				follow_string += follow_symbol.content + ' '
		file.write("%s : { %s }\n"%( follow['producer'], follow_string))


def main():
	input_file_name = "input.gra"
	output_file_name = "output.gra"
	summary_file_name = "summary.sum"
	f = open(input_file_name,"r")
	of = open(output_file_name,"w")
	sf = open(summary_file_name, "w")
	print("Taking input grammer file: %s"%(input_file_name))
	grammerRules = getGrammerRulesFromFile(f)
	doLeftFactoring(grammerRules)
	# writeGrammerToFile(removeIndirectLeftRecursion(grammerRules),of)
	
	# firsts = getFirst(grammerRules)
	# follows = getFollow(grammerRules)
	# print(follows)
	# writeSummaryToFile(firsts,follows, sf)
	# doLeftFactoring(grammerRules)

	updatedGrammer = removeLeftRecursion(grammerRules)
	if len(updatedGrammer):
		print("Grammer is recursive at: ", updatedGrammer['recursive_at'])
		print("After Removal of Left Recursion: ")
		print(updatedGrammer['grammerRules'])
		writeGrammerToFile(updatedGrammer['grammerRules'], of)
	else:
		print("Non changes in grammer")

if __name__ == '__main__':
	main()