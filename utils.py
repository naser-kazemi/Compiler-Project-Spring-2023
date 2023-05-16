# token types
from collections import OrderedDict, defaultdict
from enum import Enum
import json


class TokenType(Enum):
    NUM = 'NUM'
    IDorKEYWORD = 'IDorKEYWORD'
    ID = 'ID'
    KEYWORD = 'KEYWORD'
    SYMBOL = 'SYMBOL'
    COMMENT = 'COMMENT'
    WHITESPACE = 'WHITESPACE'
    INVALID = 'INVALID'
    UNMATCHED_COMMENT = 'UNMATCHED_COMMENT'

    # reserved words
    IF = 'if'
    ELSE = 'else'
    VOID = 'void'
    INT = 'int'
    REPEAT = 'repeat'
    BREAK = 'break'
    UNTIL = 'until'
    RETURN = 'return'

    def __str__(self):
        return self.value


rule_dict = {
    "Program": [["Declaration-list"]],
    "Declaration-list": [["Declaration", "Declaration-list"], ['epsilon']],
    "Declaration": [["Declaration-initial", "Declaration-prime"]],
    "Declaration-initial": [["Type-specifier", "ID"]],
    "Declaration-prime": [["Fun-declaration-prime"], ["Var-declaration-prime"]],
    "Var-declaration-prime": [[";"], ["[", "NUM", "]", ";"]],
    "Fun-declaration-prime": [["(", "Params", ")", "Compound-stmt"]],
    "Type-specifier": [["int"], ["void"]],
    "Params": [["int", "ID", "Param-prime", "Param-list"], ["void"]],
    "Param-list": [[",", "Param", "Param-list"], ['epsilon']],
    "Param": [["Declaration-initial", "Param-prime"]],
    "Param-prime": [["[", "]"], ['epsilon']],
    "Compound-stmt": [["{", "Declaration-list", "Statement-list", "}"]],
    "Statement-list": [["Statement", "Statement-list"], ['epsilon']],
    "Statement": [["Expression-stmt"], ["Compound-stmt"], ["Selection-stmt"], ["Iteration-stmt"], ["Return-stmt"]],
    "Expression-stmt": [["Expression", ";"], ["break", ";"], [";"]],
    "Selection-stmt": [["if", "(", "Expression", ")", "Statement", "else", "Statement"]],
    "Iteration-stmt": [["repeat", "Statement", "until", "(", "Expression", ")"]],
    "Return-stmt": [["return", "Return-stmt-prime"]],
    "Return-stmt-prime": [[";"], ["Expression", ";"]],
    "Expression": [["Simple-expression-zegond"], ["ID", "B"]],
    "B": [["=", "Expression"], ["[", "Expression", "]", "H"], ["Simple-expression-prime"]],
    "H": [["=", "Expression"], ["G", "D", "C"]],
    "Simple-expression-zegond": [["Additive-expression-zegond", "C"]],
    "Simple-expression-prime": [["Additive-expression-prime", "C"]],
    "C": [["Relop", "Additive-expression"], ['epsilon']],
    "Relop": [["<"], ["=="]],
    "Additive-expression": [["Term", "D"]],
    "Additive-expression-prime": [["Term-prime", "D"]],
    "Additive-expression-zegond": [["Term-zegond", "D"]],
    "D": [["Addop", "Term", "D"], ['epsilon']],
    "Addop": [["+"], ["-"]],
    "Term": [["Factor", "G"]],
    "Term-prime": [["Factor-prime", "G"]],
    "Term-zegond": [["Factor-zegond", "G"]],
    "G": [["*", "Factor", "G"], ['epsilon']],
    "Factor": [["(", "Expression", ")"], ["ID", "Var-call-prime"], ["NUM"]],
    "Var-call-prime": [["(", "Args", ")"], ["Var-prime"]],
    "Var-prime": [["[", "Expression", "]"], ['epsilon']],
    "Factor-prime": [["(", "Args", ")"], ['epsilon']],
    "Factor-zegond": [["(", "Expression", ")"], ["NUM"]],
    "Args": [["Arg-list"], ['epsilon']],
    "Arg-list": [["Expression", "Arg-list-prime"]],
    "Arg-list-prime": [[",", "Expression", "Arg-list-prime"], ['epsilon']]
}


def get_token_type(char):
    if char.isdigit():
        return TokenType.NUM
    if char.isalnum():
        return TokenType.IDorKEYWORD
    if char in ['+', '-', '*', '(', ')', '{', '}', '[', ']', ',', ';', '=', '<', '>']:
        return TokenType.SYMBOL
    if char in [' ', '\t', '\n', '\r', '\v', '\f', '']:
        return TokenType.WHITESPACE
    if char == '/':
        return TokenType.COMMENT
    return TokenType.INVALID


def print_short_comment(comment):
    return comment[:7] + '...' if len(comment) > 7 else comment


def read_grammar_data():
    with open("data.json", "r") as f:
        data = json.load(f)
        terminals = data["terminals"]
        non_terminals = data["non-terminals"]
        first = data["first"]
        follow = data["follow"]
        return terminals, non_terminals, first, follow


class Node:

    def __init__(self, name):
        self.name = name
        self.child = None

    def add_child(self, child):
        self.child = child


class TransitionDiagram:

    def __init__(self, rule):
        self.rule = rule
        self.nodes = []
        self.start = None
        self.accept = None
        self.createTD()

    def createTD(self):
        self.start = self.rule[0]
        rhs = self.rule[1]

