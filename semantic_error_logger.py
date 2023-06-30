from utils import *


class SemanticErrorLogger:
    def __init__(self):
        self.errors = []

    def scope_check(self, lookahead):
        ...

    def void_check(self, var_id):
        ...

    def break_check(self, lookahead):
        ...

    def type_mismatch(self, lookahead, operand_1, operand_2):
        ...

    def parameter_num_matching(self, lookahead, args, attributes):
        ...

    def parameter_type_matching(self, lookahead, var, arg, num):
        ...

    def get_func_name(self, var):
        ...
