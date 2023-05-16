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
