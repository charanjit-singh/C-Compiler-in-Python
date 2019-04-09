"""
	Author: Charanjit Singh
	Website: https://charanjit-singh.github.io

	Description: Constants used while analysing or compiling the source file.

"""

KEYWORDS = (
	"auto",
	"break",
	"case",
	"char",
	"const",
	"continue",
	"default",
	"do",
	"double",
	"else",
	"enum",
	"extern",
	"float",
	"for",
	"goto",
	"if",
	"inline",
	"int",
	"long",
	"register",
	"restrict",
	"return",
	"short",
	"signed",
	"sizeof",
	"static",
	"struct",
	"switch",
	"typedef",
	"union",
	"unsigned",
	"void",
	"this",
	"volatile",
	"while",
	"_Bool",
	"_Complex",
	"_Imaginary"
)

def get_keywords_regex():
	regex = "("
	for keyword in KEYWORDS:
		regex += "(%s)|"%(keyword)
	regex = regex[:-1]
	regex += ")"
	return regex


PUNCTUATORS = (
	"{",
	"}",
	"[",
	"]",
	",",
	".",
	";",
	"(",
	")",
	"<",
	">",
	"<=",
	">=",
	"++",
	"--",
	"+",
	"-",
	"*",
	"/",
	"+=",
	"-=",
	"*=",
	"/=",
	"%",
	"&",
	"!",
	"!=",
	"|",
	"|=",
	"||",
	"&&",
	"?",
	"=",
	"->",
	"==",
	"<%",
	"%>"
)

def get_punctuators_regex():
	regex = "("
	for PUNCTUATOR in PUNCTUATORS:
		tempPunc = ""
		for m in PUNCTUATOR:
			if m in ['?', '+', '.', '*', '{', '}', ')', '(', '[', ']', '|']:
				tempPunc += "\\"
			tempPunc += m
		regex += "(%s)|"%(tempPunc)
	regex = regex[:-1]
	regex += ")"
	return regex