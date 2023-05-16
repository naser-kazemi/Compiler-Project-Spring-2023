from utils import *
from scanner import Scanner

transitionDiagrams = {}

def main():
    terminals, non_terminals, first, follow = read_grammar_data()
    print("Terminals:", terminals)
    print("Non-terminals:", non_terminals)
    print("First:", first)
    print("Follow:", follow)

def createTD():
    for x in rule_dict.items():
        td = TransitionDiagram(x)
        transitionDiagrams[td.lhs] = td
    

def parse():
    token = Scanner.get_next_token()







def makeTree(scanner):
    pass


if __name__ == '__main__':
    main()
