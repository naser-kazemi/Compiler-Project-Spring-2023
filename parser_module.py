from utils import read_grammar_data
from scanner import Scanner


def main():
    terminals, non_terminals, first, follow = read_grammar_data()
    print("Terminals:", terminals)
    print("Non-terminals:", non_terminals)
    print("First:", first)
    print("Follow:", follow)


if __name__ == '__main__':
    main()
