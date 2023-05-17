from utils import *
from scanner import Scanner

START_PRODUCTION_RULE = "Program"
NON_TERMINAL = "NON_TERMINAL"
SKIP = "SKIP"
MATCH = "MATCH"
MISMATCH = "MISMATCH"


class Parser:
    def __init__(self, scanner, rule_dict):
        self.scanner = scanner
        self.rule_dict = rule_dict
        self.transitionDiagrams = {}
        self.createTDs()
        self.stack = []
        self.terminals, self.non_terminals, self.first, self.follow = read_grammar_data()
        self.root = None

    def createTDs(self):
        for x in self.rule_dict.items():
            td = TransitionDiagram(x)
            self.transitionDiagrams[td.lhs] = td

    def get_next_token(self):
        token = self.scanner.get_next_token()
        while token.type == TokenType.WHITESPACE or token.type == TokenType.COMMENT:
            token = self.get_next_token()
        return token

    def get_terminal_transition(self, token, state):
        transitions = state.outs
        is_all_terminal = all(tr.value in self.terminals for tr in transitions)
        for tr in transitions:
            if tr.value in self.terminals and tr.value == token.value:
                return True, tr
        if is_all_terminal:
            return False, transitions[0]
        return NON_TERMINAL

    def get_non_terminal_transition(self, token, state):
        non_terminals = [tr for tr in state.outs if tr.value in self.non_terminals]
        for tr in non_terminals:
            if token.value in self.first[tr.value]:
                return MATCH, tr
        for tr in non_terminals:
            if EPSILON in self.first[tr.value] and token.value in self.follow[tr.value]:
                return SKIP, tr

        return MISMATCH, non_terminals[0]

    def non_terminal_transition_error(self, token, transition):
        if token.value in self.follow[transition.value]:
            return True, f"missing {transition.value} on line {token.line_num}."
        return False, f"illegal {token.value} found on line {token.line_num}."

    def parse(self):
        start_td = self.transitionDiagrams[START_PRODUCTION_RULE]
        self.stack.append(start_td.start)
        current_node = None
        current_state = self.stack[0]
        current_transition = "Program"
        token = self.get_next_token()
        print(token.value, token.type)
        while self.stack:
            print(current_state.name)
            current_node = Node(current_transition, parent=current_node)
            if self.root is None:
                self.root = current_node
            transition = self.get_terminal_transition(token, current_state)
            if transition != NON_TERMINAL:
                is_matched, tr = transition
                if is_matched:
                    token = self.get_next_token()
                    self.stack.pop()
                    self.stack.append(tr.end)
                    current_state = self.stack[-1]
                    current_transition = (token.type, token.type)
                else:
                    print(f"missing {tr.value} on line {token.line_num}")
                    self.stack.pop()
                    self.stack.append(tr.end)
                    current_state = self.stack[-1]

            else:
                match_result, transition = self.get_non_terminal_transition(token, current_state)
                if match_result == MISMATCH:
                    is_in_follow, error = self.non_terminal_transition_error(token, transition)
                    if is_in_follow:
                        current_state = transition.end
                        self.stack.pop()
                        self.stack.append(current_state)
                    else:
                        token = self.get_next_token()
                        self.stack.pop()
                        self.stack.append(transition.end)
                        td = self.transitionDiagrams[transition.value]
                        self.stack.append(td.start)
                        current_state = self.stack[-1]
                    print(error)
                else:
                    if match_result == MATCH:
                        self.stack.pop()
                        self.stack.append(transition.end)
                        td = self.transitionDiagrams[transition.value]
                        self.stack.append(td.start)
                        current_state = self.stack[-1]
                    else:
                        current_state = transition.end
                        self.stack.pop()
                        self.stack.append(current_state)
            if current_state.name == "accept":
                current_state = self.stack.pop()


def main():
    terminals, non_terminals, first, follow = read_grammar_data()
    print("Terminals:", terminals)
    print("Non-terminals:", non_terminals)
    print("First:", first)
    print("Follow:", follow)


def makeTree(scanner):
    pass


if __name__ == '__main__':
    main()
