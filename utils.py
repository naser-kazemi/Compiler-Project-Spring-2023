from enum import Enum
import json
import anytree
from anytree import Node, RenderTree


class TokenType(Enum):
    NUM = "NUM"
    IDorKEYWORD = "IDorKEYWORD"
    ID = "ID"
    KEYWORD = "KEYWORD"
    SYMBOL = "SYMBOL"
    COMMENT = "COMMENT"
    WHITESPACE = "WHITESPACE"
    INVALID = "INVALID"
    UNMATCHED_COMMENT = "UNMATCHED_COMMENT"

    IF = "if"
    ELSE = "else"
    VOID = "void"
    INT = "int"
    REPEAT = "repeat"
    BREAK = "break"
    UNTIL = "until"
    RETURN = "return"

    def __str__(self):
        return self.value


def write_lexical_errors(scanner, output_file):
    with open(output_file + "lexical_errors.txt", "w") as f:
        if len(scanner.LEXICAL_ERRORS) == 0:
            f.write("There is no lexical error.")
        else:
            for line in scanner.LEXICAL_ERRORS:
                f.write(f"{line}.\t")
                for error in scanner.LEXICAL_ERRORS[line]:
                    f.write(f"({error[0]}, {error[1]}) ")
                f.write("\n")


def write_symbol_table(scanner, output_file):
    with open(output_file + "symbol_table.txt", "w") as f:
        symbols = scanner.SYMBOL_TABLE["keyword"].copy()
        symbols.extend(scanner.SYMBOL_TABLE["names"])
        for i, symbol in enumerate(symbols):
            f.write(f"{i + 1}.\t{symbol}\n")


def write_tokens(scanner, output_file):
    with open(output_file + "tokens.txt", "w") as f:
        for line in scanner.tokens:
            if len(scanner.tokens[line]) == 0:
                continue
            f.write(f"{line}.\t")
            for token in scanner.tokens[line]:
                f.write("(" + str(token.type) + ", " + token.value + ") ")
            f.write("\n")


EPSILON = "epsilon"


def get_token_type(char):
    if char.isdigit():
        return TokenType.NUM
    if char.isalnum() or char == "_":
        return TokenType.IDorKEYWORD
    if char in ["+", "-", "*", "(", ")", "{", "}", "[", "]", ",", ";", "=", "<", ">"]:
        return TokenType.SYMBOL
    if char in [" ", "\t", "\n", "\r", "\v", "\f", ""]:
        return TokenType.WHITESPACE
    if char == "/":
        return TokenType.COMMENT
    return TokenType.INVALID


def get_token_type_for_grammar(token):
    if token.type == TokenType.KEYWORD:
        return str(token.value)
    if token.type == TokenType.SYMBOL:
        return str(token.value)
    if token.value == "$":
        return "$"
    return str(token.type)


def print_short_comment(comment):
    return comment[:7] + "..." if len(comment) > 7 else comment


def read_grammar_data():
    with open("assets/data.json", "r") as f:
        data = json.load(f)
        terminals = data["terminals"]
        non_terminals = data["non-terminals"]
        first = data["first"]
        follow = data["follow"]
        return terminals, non_terminals, first, follow


def convert_grammar_to_rule_dict(filename):
    rules = {}
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            lhs, rhs = line.split("->")
            lhs = lhs.strip()
            rhs = rhs.strip()
            if lhs not in rules:
                rules[lhs] = []
            rhs = rhs.split(" ")
            rhs = [x.strip() for x in rhs]
            rules[lhs].append(rhs)
    return rules


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

    def traverse(self, node, rule):
        for edge in node.outs:
            rule[-1].append(edge.value)
            next = edge.end
            if next is not self.accept:
                self.traverse(next, rule)

    def derive_rules(self):
        rules = [self.lhs]
        for next in self.start.outs:
            rules.append([next.value])
            self.traverse(next.end, rules)
        return rules[0], rules[1:]


class ActionSymbol(Enum):
    Output = "output"
    JpFrom = "jp_from"
    InitRf = "init_rf"
    Pid = "pid"
    Pnum = "pnum"
    Prv = "prv"
    Parray = "parray"
    Ptype = "ptype"
    Pop = "pop"
    DeclareArray = "declare_array"
    ArrayType = "array_type"
    DeclareFunction = "declare_function"
    CaptureParamType = "capture_param_type"
    DeclareId = "declare_id"
    Declare = "declare"
    Assign = "assign"
    OpExec = "op_exec"
    OpPush = "op_push"
    Hold = "hold"
    Label = "label"
    Decide = "decide"
    JpfRepeat = "jpf_repeat"
    FunctionCall = "function_call"
    FunctionReturn = "function_return"
    ArgInit = "arg_init"
    ArgFinish = "arg_finish"
    ArgPass = "arg_pass"
    FunctionScope = "function_scope"
    ContainerScope = "container_scope"
    TemporaryScope = "temporary_scope"
    SimpleScope = "simple_scope"
    ScopeStart = "scope_start"
    ScopeEnd = "scope_end"
    Prison = "prison"
    PrisonBreak = "prison_break"
    ExecMain = "exec_main"
    SetMainRa = "set_main_ra"
    CheckDeclarationType = "check_declaration_type"
    CheckInContainer = "check_in_container"

    def __str__(self) -> str:
        return f"#{self.value}"


class Operation(Enum):
    Add = "ADD"
    Mult = "MULT"
    Sub = "SUB"
    Eq = "EQ"
    Lt = "LT"
    Assign = "ASSIGN"
    Jpf = "JPF"
    Jp = "JP"
    Print = "PRINT"
    Empty = ""

    @staticmethod
    def get_operation(symbol):
        return OPERATIONS.get(symbol, Operation.Empty)

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.__repr__()


OPERATIONS: dict[str, Operation] = {
    "+": Operation.Add,
    "*": Operation.Mult,
    "-": Operation.Sub,
    "==": Operation.Eq,
    "<": Operation.Lt,
}

RETURN = "RETURN"
BREAK = "BREAK"


def last_index_of(lst, item):
    return len(lst) - 1 - lst[::-1].index(item)
