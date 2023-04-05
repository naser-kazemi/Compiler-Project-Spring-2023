# token types
from collections import OrderedDict, defaultdict
from enum import Enum


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


def get_token_type(char):
    if char.isdigit():
        return TokenType.NUM
    if char.isalnum():
        return TokenType.IDorKEYWORD
    if char in ['+', '-', '*', '%', '(', ')', '{', '}', '[', ']', ',', ';', '=', '<', '>']:
        return TokenType.SYMBOL
    if char in [' ', '\t', '\n', '\r', '\v', '\f', '']:
        return TokenType.WHITESPACE
    if char == '/':
        return TokenType.COMMENT
    return TokenType.INVALID


def print_short_comment(comment):
    return comment[:4] + '...' if len(comment) > 7 else comment
