"""
	Author: Charanjit Singh
	Website: https://charanjit-singh.github.io

	Data Type: Token 
	Description: Lexical Token. Instead of storing token information in 'symbol_table',
				 this 'Token' will be storing the extra information in it's fields.

"""

class Token():
	"""
		extras stores additional information.
		'Token Types' are from 'C Draft'.
	"""
	TYPE_IDENTIFIER = 0
	TYPE_KEYWORD = 1
	TYPE_CONSTANT = 2
	TYPE_STRING_LITERAL = 3
	TYPE_CHAR_CONST = 4
	TYPE_PUNCTUATOR = 5
	TYPE_COMMENT = 5
	TYPE_UNKNOWN = 16

	def __init__(self, _type, lexene ):
		self.type = _type
		self.lexene = lexene
		self.extras = {}

