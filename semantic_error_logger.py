from utils import *
from scanner import Scanner, Token


class SemanticErrorLogger:
    def __init__(self, scanner):
        self.scanner = scanner
        self.errors = []

    def scope_check(self, token, scope):
        if token.value == "output":
            return
        address = None
        for record in self.scanner.SYMBOL_TABLE["ids"][::-1]:
            if record.id == token.value and record.scope <= scope:
                address = record.address
                break
        if address is None:
            self.errors.append(
                f"#{token.line_num}: Semantic Error! '{token.value}' is not defined."
            )

    def void_check(self, token, var_id):
        if token.value == "void":
            self.errors.append(
                f"#{token.line_num}: Semantic Error! Illegal type of void for '{var_id}'."
            )

    # (array_id, 'int*', address, self.current_scope)
    def get_operand_type(self, operand):
        if operand.startswith("#"):
            return "int"
        for record in self.scanner.SYMBOL_TABLE["ids"]:
            if record.address == operand:
                return record.type
        return "int"

    def break_check(self, break_stack, token):
        if len(break_stack) <= 0:
            self.errors.append(
                f"#{token.line_num - 1}: Semantic Error! No 'repeat ... until' found for 'break'."
            )

    def type_mismatch(self, token, operand_1, operand_2):
        if operand_1 is None or operand_2 is None:
            return
        operand_1_type = self.get_operand_type(operand_1)
        operand_2_type = self.get_operand_type(operand_2)
        if operand_1_type != operand_2_type:
            # TODO: we need to handle array types
            self.errors.append(
                f"#{token.line_num}: Semantic Error! Type mismatch in operands, Got"
                f" '{operand_2_type}' instead of '{operand_1_type}'."
            )

    def parameter_num_matching(self, token, args, attributes):
        ...

    def parameter_type_matching(self, token, var, arg, num):
        ...

    def get_func_name(self, var):
        ...
