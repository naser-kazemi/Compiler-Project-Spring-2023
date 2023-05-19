from utils import *
from scanner import Scanner
from parser_module import Parser
import sys


# write lexical errors
def write_lexical_errors(scanner, output_file):
    with open(output_file + 'lexical_errors.txt', 'w') as f:
        if len(scanner.LEXICAL_ERRORS) == 0:
            f.write('There is no lexical error.')
        else:
            for line in scanner.LEXICAL_ERRORS:
                f.write(f'{line}.\t')
                for error in scanner.LEXICAL_ERRORS[line]:
                    f.write(f'({error[0]}, {error[1]}) ')
                f.write('\n')


# write symbol table
def write_symbol_table(scanner, output_file):
    with open(output_file + 'symbol_table.txt', 'w') as f:
        symbols = scanner.SYMBOL_TABLE['keyword'].copy()
        symbols.extend(scanner.SYMBOL_TABLE['id'])
        for i, symbol in enumerate(symbols):
            f.write(f'{i + 1}.\t{symbol}\n')


def write_tokens(scanner, output_file):
    with open(output_file + 'tokens.txt', 'w') as f:
        for line in scanner.tokens:
            if len(scanner.tokens[line]) == 0:
                continue
            f.write(f'{line}.\t')
            for token in scanner.tokens[line]:
                f.write('(' + str(token.type) + ', ' + token.value + ') ')
            f.write('\n')


if __name__ == '__main__':
    # get argument from command line
    if len(sys.argv) < 2:
        input_dir = ''
        output_dir = ''
    else:
        input_dir = sys.argv[1] + '/'
        output_dir = 'output/' + sys.argv[2] + '/'
    scanner = Scanner(input_dir + 'input.txt')
    parser = Parser(scanner, rule_dict)
    parser.parse()
    with open("parse_tree.txt", 'w') as output:
        for pre, fill, node in RenderTree(parser.root):
            output.write("%s%s\n" % (pre, node.name))

    with open("syntax_errors.txt", 'w') as output:
        if parser.syntax_error:
            for error in parser.syntax_error:
                output.write(f"{error}\n")
        else:
            output.write("There is no syntax error.")
