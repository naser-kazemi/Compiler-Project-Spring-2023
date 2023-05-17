# token types
from collections import OrderedDict, defaultdict
from enum import Enum
import json
from anytree import Node, RenderTree


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


EPSILON = "EPSILON"

rule_dict = {
    "Program": [["Declaration-list"]],
    "Declaration-list": [["Declaration", "Declaration-list"], ['EPSILON']],
    "Declaration": [["Declaration-initial", "Declaration-prime"]],
    "Declaration-initial": [["Type-specifier", "ID"]],
    "Declaration-prime": [["Fun-declaration-prime"], ["Var-declaration-prime"]],
    "Var-declaration-prime": [[";"], ["[", "NUM", "]", ";"]],
    "Fun-declaration-prime": [["(", "Params", ")", "Compound-stmt"]],
    "Type-specifier": [["int"], ["void"]],
    "Params": [["int", "ID", "Param-prime", "Param-list"], ["void"]],
    "Param-list": [[",", "Param", "Param-list"], ['EPSILON']],
    "Param": [["Declaration-initial", "Param-prime"]],
    "Param-prime": [["[", "]"], ['EPSILON']],
    "Compound-stmt": [["{", "Declaration-list", "Statement-list", "}"]],
    "Statement-list": [["Statement", "Statement-list"], ['EPSILON']],
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
    "C": [["Relop", "Additive-expression"], ['EPSILON']],
    "Relop": [["<"], ["=="]],
    "Additive-expression": [["Term", "D"]],
    "Additive-expression-prime": [["Term-prime", "D"]],
    "Additive-expression-zegond": [["Term-zegond", "D"]],
    "D": [["Addop", "Term", "D"], ['EPSILON']],
    "Addop": [["+"], ["-"]],
    "Term": [["Factor", "G"]],
    "Term-prime": [["Factor-prime", "G"]],
    "Term-zegond": [["Factor-zegond", "G"]],
    "G": [["*", "Factor", "G"], ['EPSILON']],
    "Factor": [["(", "Expression", ")"], ["ID", "Var-call-prime"], ["NUM"]],
    "Var-call-prime": [["(", "Args", ")"], ["Var-prime"]],
    "Var-prime": [["[", "Expression", "]"], ['EPSILON']],
    "Factor-prime": [["(", "Args", ")"], ['EPSILON']],
    "Factor-zegond": [["(", "Expression", ")"], ["NUM"]],
    "Args": [["Arg-list"], ['EPSILON']],
    "Arg-list": [["Expression", "Arg-list-prime"]],
    "Arg-list-prime": [[",", "Expression", "Arg-list-prime"], ['EPSILON']]
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


class State:
    def __init__(self, name, is_terminal=False):
        self.name = name
        self.is_terminal = is_terminal
        self.ins = []
        self.outs = []


class Transition:

    def __init__(self, name, start, end):
        self.value = name
        self.start = start
        self.end = end
        start.outs.append(self)
        end.ins.append(self)


class TransitionDiagram:

    def __init__(self, rule):
        self.rule = rule
        self.lhs = rule[0]
        self.start = State(0)
        self.nodes = [self.start]
        self.counter = 0
        self.accept = State("accept", is_terminal=True)
        self.createTD()

    def createTD(self):
        rhs = self.rule[1]
        for expr in rhs:
            current = self.start
            expr_last = len(expr) - 1
            for idx, item in enumerate(expr):
                if idx == expr_last or item == EPSILON:
                    Transition(item, current, self.accept)
                else:
                    self.counter += 1
                    next = State(self.counter)
                    Transition(item, current, next)
                    self.nodes.append(next)
                    current = next

    def traverse(self, node, is_print=False):
        if is_print:
            print(node.name, end=" -> ")
            if node is self.start:
                print()

        for edge in node.outs:
            if is_print:
                print(edge.value, end=" -> ")
                next = edge.end
                if next is not self.accept:
                    self.traverse(next, is_print)
                else:
                    print(self.accept.name)

    def print_diagram(self):
        print(self.lhs + ": ")
        self.traverse(self.start, is_print=True)


if __name__ == '__main__':
    rule = "B", [["=", "Expression"], ["[", "Expression", "]", "H"], ["Simple-expression-prime"]]
    print(rule)
    transition_diagram = TransitionDiagram(rule)
    transition_diagram.print_diagram()
