from utils import *
from scanner import Scanner
from parser_module import Parser
import sys

if __name__ == "__main__":
    # get argument from command line
    if len(sys.argv) < 2:
        input_dir = ""
        output_dir = ""
    else:
        input_dir = sys.argv[1] + "/"
        output_dir = "output/" + sys.argv[2] + "/"
    scanner = Scanner(input_dir + "input.txt")
    rule_dict = convert_grammar_to_rule_dict("assets/grammar_with_actions.txt")
    parser = Parser(scanner, rule_dict)
    parser.parse()

    with open(output_dir + "semantic_errors.txt", "w") as output:
        if not parser.code_generator.error_logger.empty():
            for error in parser.code_generator.error_logger:
                output.write(f"{error}\n")
        else:
            output.write("The input program is semantically correct.")

    with open(output_dir + "output.txt", "w") as output:
        if not parser.code_generator.error_logger.empty():
            output.write("The output code has not been generated.")
        else:
            program_block = parser.code_generator.program_block.instructions
            program_block = [x for x in program_block if x is not None]
            for i, instruction in enumerate(program_block):
                output.write(
                    f"{i}\t{instruction}\n")

    # with open("parse_tree.txt", "w") as output:
    #     for pre, fill, node in RenderTree(parser.root):
    #         output.write("%s%s\n" % (pre, node.name))
    #
    # with open("syntax_errors.txt", "w") as output:
    #     if parser.syntax_error:
    #         for error in parser.syntax_error:
    #             output.write(f"{error}\n")
    #     else:
    #         output.write("There is no syntax error.")
