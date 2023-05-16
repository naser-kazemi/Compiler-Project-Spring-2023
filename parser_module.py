from utils import *
from scanner import Scanner


class Parser:
    def __init__(self, scanner, rule_dict):
        self.scanner = scanner
        self.rule_dict = rule_dict
        self.transitionDiagrams = {}
        self.createTDs()

    def createTDs(self):
        for x in self.rule_dict.items():
            td = TransitionDiagram(x)
            self.transitionDiagrams[td.lhs] = td

    def parse(self):
        token = self.scanner.get_next_token()



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
