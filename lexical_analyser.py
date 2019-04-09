from utils.Constants import *
from utils.Token import Token
import re

def compile_regex(regex_string, name):
	return (re.compile(regex_string, flags = re.MULTILINE | re.S), name)

class LexicalAnalyser():

	def __init__(self, **kwargs):
		self.input_file = kwargs.get('input_file', None)
		self.input_file_string = None
		self.token_stream = []
		self.input_file_string = self.input_file.read()
		self.f_pointer = 0
		self.file_length = len(self.input_file_string)
		self.regular_expressions = [] # lexical regular expressions ( Compiled ) 

	def analyse(self):
		identifier = '[a-zA-Z_][0-9a-zA-Z]*'
		
		# Integer Constant Regexps
		unsigned_suffix = '(u|U)'
		long_suffix = '(l|L)'
		long_long_suffix = '(ll|LL)'
		integer_suffix = '((%s[%s]?)|(%s%s)|(%s(%s)?)|(%s(%s)?))'%(unsigned_suffix, long_suffix, 
																unsigned_suffix, long_long_suffix,
																long_suffix, unsigned_suffix,
																long_long_suffix, unsigned_suffix)
		"""
			integer-suffix:
				unsigned-suffix long-suffix[opt]
				unsigned-suffix long-long-suffix
				long-suffix unsigned-suffix[opt]
				long-long-suffix unsigned-suffix[opt]
		"""

		non_zero_digit = '([1-9])'
		octal_digit = '([0-7])'
		hexadecimal_prefix = '(0[x|X])'
		hexadecimal_digit = '([0-9]|[a-f]|[A-F])'
		digit = '([0-9])'
		decimal_constant = '(%s%s*)'%(non_zero_digit, digit)
		octal_constant = '(0%s*)'%(octal_digit)
		hexadecimal_constant = '(%s?%s+)'%(hexadecimal_prefix, hexadecimal_digit)
		integer_constant = '((%s|%s|%s)%s?)'%(decimal_constant, hexadecimal_constant, octal_constant, integer_suffix)

		# Floating Constant
		sign = '([\+|-])'
		digit_sequence = '(%s+)'%(digit)
		exponent_part = '([e|E]%s?%s)'%(sign, digit_sequence)
		floating_suffix = '([f|F|l|L])'
		fractional_constant = '((%s?\.%s|%s\.))'%(digit_sequence, digit_sequence, digit_sequence)
		decimal_floating_constant = '((%s%s?%s?)|(%s%s%s))'%(fractional_constant, exponent_part, floating_suffix,
														digit_sequence, exponent_part, floating_suffix)
		
		hexadecimal_digit_sequence = '(%s+)'%(hexadecimal_digit)
		hexadecimal_fractional_constant = '((%s?\.%s)|(%s\.))'%(hexadecimal_digit_sequence, hexadecimal_digit_sequence,
														hexadecimal_digit_sequence)
		binary_exponent_part = '([pP]%s?%s)'%(sign, digit_sequence)

		hexadecimal_floating_constant = '((%s%s%s%s?)|(%s%s%s%s?))'%(hexadecimal_prefix, hexadecimal_fractional_constant, binary_exponent_part, floating_suffix,
																	hexadecimal_prefix, hexadecimal_digit_sequence, binary_exponent_part, floating_suffix )
		"""
			hexadecimal-floating-constant:
				hexadecimal-prefix hexadecimal-fractional-constant binary-exponent-part floating-suffix[opt]
				hexadecimal-prefix hexadecimal-digit-sequence  binary-exponent-part floating-suffix[opt]
		"""
		
		floating_constant = '(%s|%s)'%(decimal_floating_constant, hexadecimal_fractional_constant)

		string_literal = '(".*")'
		character_constant = "('.*')"

		keywords_regex = get_keywords_regex()
		punctuators_regex = get_punctuators_regex()

		self.regular_expressions.append(compile_regex(string_literal, 'string_literal'))
		self.regular_expressions.append(compile_regex(character_constant,'character_constant'))
		self.regular_expressions.append(compile_regex(punctuators_regex, 'punctuator'))
		self.regular_expressions.append(compile_regex(floating_constant,'floating_constant'))
		self.regular_expressions.append(compile_regex(integer_constant,'integer_constant'))
		self.regular_expressions.append(compile_regex(keywords_regex, 'keyword'))
		self.regular_expressions.append(compile_regex(identifier,'identifier'))

		while True:
			token = self.get_next_token()
			if not token:
				break

	def get_next_token(self):
		f_pointer = self.f_pointer
		ignored_regexp = re.compile('[\s\t\n]+')
		while f_pointer < self.file_length:
			data_part = self.input_file_string[f_pointer:]
			matches = []
			# TODO: Check for strings and char constants
			for ( regexp, name ) in self.regular_expressions:
				m = regexp.match(data_part)
				if not m:
					continue
				start, end = m.span()
				last_index = f_pointer + end 
				if last_index < self.file_length:
					if not name == 'punctuator' and not self.is_separator(data_part[end]):
						continue

				matches.append((m, name))
				break

			if len(matches):
				match = matches[0]
				start, end = match[0].span()
				print(match[1], match[0].group(), '\n----------')
				self.f_pointer = f_pointer + end 
				return match
			else:
				f_pointer +=1



	def get_token_stream(self):
		pass

	def print_token_stream(self):
		pass

	def is_separator(self, character):
		return character in (' ', '\n', '\t') + PUNCTUATORS
		