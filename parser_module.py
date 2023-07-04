from utils import *
from scanner import Scanner, Token
from codegen import CodeGenerator

START_PRODUCTION_RULE = "Program"
NON_TERMINAL = "NON_TERMINAL"
SKIP = "SKIP"
MATCH = "MATCH"
MISMATCH = "MISMATCH"


class Parser:
    def __init__(self, scanner, rule_dict):
        self.scanner = scanner
        self.code_generator = CodeGenerator(self.scanner)
        self.rule_dict = rule_dict
        self.transitionDiagrams = {}
        self.createTDs()
        self.stack = []
        (
            self.terminals,
            self.non_terminals,
            self.first,
            self.follow,
        ) = read_grammar_data()
        self.root = None
        self.syntax_error = []

    def createTDs(self):
        for x in self.rule_dict.items():
            td = TransitionDiagram(x)
            self.transitionDiagrams[td.lhs] = td

    def compute_first(self, rhs):
        first_list = []
        for item in rhs:
            if item.startswith("#"):
                continue
            if item in self.terminals:
                first_list.append(item)
                return first_list
            elif item == EPSILON:
                continue
            else:
                first = self.first[item].copy()
                if EPSILON in first:
                    first.remove(EPSILON)
                first_list.extend(first)
                if EPSILON not in self.first[item]:
                    return first_list
        first_list.append(EPSILON)
        return first_list

    def get_next_token(self):
        token = self.scanner.get_next_token()
        # print(token)
        while token is None or token.type == TokenType.WHITESPACE or token.type == TokenType.COMMENT:
            token = self.get_next_token()
        return token

    def non_terminal_transition_error(self, token, transition):
        if token.value in self.follow[transition.value]:
            return True, f"#{token.line_num} : syntax error, missing {transition.value}"
        return False, f"#{token.line_num} : syntax error, illegal {token.value}"

    def get_path_on_diagram(self, token, transition_diagram):
        lhs, rhs = transition_diagram.derive_rules()
        for expr in rhs:
            if get_token_type_for_grammar(token) in self.compute_first(expr):
                return expr
        for expr in rhs:
            if EPSILON in self.compute_first(expr):
                if get_token_type_for_grammar(token) in self.follow[lhs]:
                    return expr
        if token.value == "$" and "$" in self.follow[lhs]:
            for expr in rhs:
                if EPSILON in self.compute_first(expr):
                    if get_token_type_for_grammar(token) in self.follow[lhs]:
                        return expr

        return None

    def parse(self):
        is_eof = False
        token = self.get_next_token()
        self.stack.append(("Program", None))
        while self.stack[-1][0] != "$":
            current_expression = self.stack[-1][0]

            # TODO: check if current_expression is action symbol or not
            if current_expression.startswith("#"):
                self.code_generator.call_routine(current_expression, token)
                self.stack.pop()
                continue
            if (
                    current_expression not in self.non_terminals
                    or current_expression == EPSILON
            ):
                if (
                        get_token_type_for_grammar(token) == current_expression
                        or current_expression == EPSILON
                ):
                    current_node, parent = self.stack.pop()
                    if current_expression == EPSILON:
                        Node(current_expression, parent)
                    else:
                        Node(f"({str(token.type)}, {token.value})", parent=parent)
                        token = self.get_next_token()
                else:
                    self.stack.pop()
                    self.syntax_error.append(
                        f"#{token.line_num} : syntax error, missing {current_expression}"
                    )
            else:
                transition_diagram = self.transitionDiagrams[current_expression]
                path_on_diagram = self.get_path_on_diagram(token, transition_diagram)
                if path_on_diagram is not None:
                    current_node, parent = self.stack.pop()
                    parent = Node(current_node, parent=parent)
                    if current_node == "Program":
                        self.root = parent
                        self.stack.append(("$", parent))
                    for item in path_on_diagram[::-1]:
                        self.stack.append((item, parent))
                else:
                    if token.value == "$" and len(self.stack) > 1:
                        self.syntax_error.append(
                            f"#{token.line_num} : syntax error, Unexpected EOF"
                        )
                        is_eof = True
                        break
                    if (
                            get_token_type_for_grammar(token)
                            in self.follow[current_expression]
                    ):
                        self.stack.pop()
                        self.syntax_error.append(
                            f"#{token.line_num} : syntax error, missing {current_expression}"
                        )
                    else:
                        self.syntax_error.append(
                            f"#{token.line_num} : syntax error, illegal {get_token_type_for_grammar(token)}"
                        )
                        token = self.get_next_token()
        if not is_eof:
            Node("$", self.root)


def main():
    terminals, non_terminals, first, follow = read_grammar_data()
    print("Terminals:", terminals)
    print("Non-terminals:", non_terminals)
    print("First:", first)
    print("Follow:", follow)


if __name__ == "__main__":
    main()
