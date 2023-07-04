from utils import *
from scanner import Scanner, Token, SymbolTableEntry, FunctionRecordEntry


class SemanticErrorLogger:
    def __init__(self, scanner):
        self.scanner = scanner
        self.errors = []

    def append(self, error):
        self.errors.append(error)

    def __setitem__(self, key, value):
        self.errors[key] = value

    def __getitem__(self, key):
        return self.errors[key]

    def empty(self):
        return len(self.errors) == 0

    def scope_check(self, token, scope):
        if token.value == "output":
            return
        address = None
        for record in self.scanner.SYMBOL_TABLE["id"][::-1]:
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

    def get_operand_type(self, operand):
        # print(operand)
        if operand.startswith("#"):
            return "int"
        for record in self.scanner.SYMBOL_TABLE["id"]:
            if record.address == operand:
                # print("+++++++++++++++")
                # print("===============")
                # print(operand)
                # print(record)
                # print("===============")
                # print("+++++++++++++++")
                return "array" if record.type == "int*" else record.type
        return "int"

    def break_check(self, break_stack, token):
        # print(break_stack)
        if len(break_stack) <= 0 or BREAK not in break_stack:
            self.errors.append(
                f"#{token.line_num}: Semantic Error! No 'repeat ... until' found for 'break'."
            )

    def type_mismatch(self, token, operand_1, operand_2, mult=False):
        if mult:
            self.check_type_mult(token, operand_1, operand_2)
            return
        if operand_1 is None or operand_2 is None:
            return
        operand_1_type = self.get_operand_type(operand_1)
        operand_2_type = self.get_operand_type(operand_2)
        # print(operand_1, operand_2)
        # print(operand_1_type, operand_2_type)
        if operand_1_type != operand_2_type:
            # print(operand_1_type, operand_2_type)
            # print(operand_1, operand_2)
            # print(f"#{token.line_num}: Semantic Error! Type mismatch in operands, Got"
            # f" {operand_2_type} instead of {operand_1_type}.")
            # TODO: we need to handle array types
            self.errors.append(
                f"#{token.line_num}: Semantic Error! Type mismatch in operands, Got"
                f" {operand_2_type} instead of {operand_1_type}."
            )

    def parameter_num_matching(self, token, args, function_record):
        func_name = function_record.id
        func_args = function_record.args
        if len(args) != len(func_args):
            self.errors.append(
                f"#{token.line_num}: Semantic Error! Mismatch in numbers of arguments of '{func_name}'."
            )

    def parameter_type_matching(self, token, var, arg, num):
        if arg.startswith("#"):
            if var.type != "int":
                var_type = "array" if var.type == "int*" else var.type
                self.errors.append(
                    f"#{token.line_num}: Semantic Error! Mismatch in type of argument {num} of"
                    f" '{self.get_func_name(var)}'. Expected '{var_type}' but got 'int' instead."
                )
        else:
            for record in self.scanner.SYMBOL_TABLE["id"]:
                if record.address == arg and record.type != var.type:
                    var_type = "array" if var.type == "int*" else var.type
                    record_type = "array" if record.type == "int*" else record.type
                    self.errors.append(
                        f"#{token.line_num}: Semantic Error! Mismatch in type of argument {num} of"
                        f" '{self.get_func_name(var)}'. Expected '{var_type}' but got '{record_type}' instead."
                    )

    def get_func_name(self, var):
        for record in self.scanner.SYMBOL_TABLE["id"]:
            if isinstance(record, FunctionRecordEntry):
                for arg in record.args:
                    if arg.address == var.address:
                        return record.id
        return None

    def check_type_mult(self, token, operand_1, operand_2):
        if operand_1 is None or operand_2 is None:
            return
        operand_1_type = self.get_operand_type(operand_1)
        operand_2_type = self.get_operand_type(operand_2)
        if operand_1_type != operand_2_type:
            if operand_1_type == "array":
                operand_2_type, operand_1_type = operand_1_type, operand_2_type
            self.errors.append(
                f"#{token.line_num}: Semantic Error! Type mismatch in operands, Got"
                f" {operand_2_type} instead of {operand_1_type}."
            )
