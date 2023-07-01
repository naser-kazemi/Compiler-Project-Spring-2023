from utils import *
from pb import Instruction, ProgramBlock
from semantic_stack import StackEntry, SemanticStack
from semantic_error_logger import SemanticErrorLogger
from scanner import Scanner, Token, SymbolTableEntry


class CodeGenerator:
    def __init__(self, scanner):
        self.semantic_stack = SemanticStack()
        self.program_block = ProgramBlock()
        self.scanner = scanner
        self.break_stack = []
        self.return_stack = []
        self.index = 0
        self.current_scope = 0
        self.temp_address = 5000
        self.token = None
        self.error_logger = SemanticErrorLogger(self.scanner)

    def call_routine(self, name, token):
        name = name.replace("#", "")
        self.__getattribute__(name)(token)

    def insert_instruction(self, opcode, operand1, operand2="", operand3=""):
        instruction = Instruction(opcode, operand1, operand2, operand3)
        self.program_block.append(instruction)
        self.index += 1

    def find_address(self, item):
        if item == "output":
            return item
        for record in self.scanner.SYMBOL_TABLE["id"][::-1]:
            if record.id == item:
                return record.address

    def get_temp(self, count=1):
        for _ in range(count):
            self.insert_instruction(Operation.Assign, "#0", str(self.temp_address))
            self.temp_address += 4
        return str(self.temp_address - 4 * count)

    def def_var(self, token):
        var_id = self.semantic_stack.pop()
        # TODO: void check
        self.error_logger.void_check(self.token, var_id)
        address = self.get_temp()
        self.scanner.SYMBOL_TABLE["id"].append(
            SymbolTableEntry(var_id, "int", address, self.current_scope)
        )

    def def_arr(self, token):
        arr_size, arr_id = self.semantic_stack.pop(), self.semantic_stack.pop()
        arr_size = int(arr_size[1:])
        # TODO: void check
        self.error_logger.void_check(self.token, arr_id)
        address = self.get_temp()
        array_space = self.get_temp(arr_size)
        self.insert_instruction(Operation.Assign, f"#{array_space}", address)
        self.scanner.SYMBOL_TABLE["id"].append(
            SymbolTableEntry(arr_id, "int*", address, self.current_scope)
        )

    def get_id(self, token):
        self.token = token

    def pid(self, token):
        self.semantic_stack.push(token.value)

    def pnum(self, token):
        self.semantic_stack.push(f"#{token.value}")

    def pid_addr(self, token):
        # TODO: scope check
        self.error_logger.scope_check(token, self.current_scope)
        self.semantic_stack.push(self.find_address(token.value))

    def push_opr(self, token):
        self.semantic_stack.push(token.value)

    def save_opr(self, token):
        operand2, operator, operand1 = (
            self.semantic_stack.pop(),
            self.semantic_stack.pop(),
            self.semantic_stack.pop(),
        )
        # TODO: type check
        self.error_logger.type_mismatch(token, operand1, operand2)
        address = self.get_temp()
        self.insert_instruction(
            Operation.get_operation(operator), operand1, operand2, address
        )
        self.semantic_stack.push(address)

    def assign_opr(self, token):
        operand1, operand2 = self.semantic_stack.top(), self.semantic_stack.top(1)
        self.insert_instruction(Operation.Assign, operand1, operand2)
        self.semantic_stack.pop()

    def mult_opr(self, token):
        result = self.get_temp()
        operand1, operand2 = self.semantic_stack.pop(), self.semantic_stack.pop()
        self.insert_instruction(Operation.Mult, operand1, operand2, result)
        self.semantic_stack.push(result)

    def arr_idx(self, token):
        idx, arr_id = self.semantic_stack.pop(), self.semantic_stack.pop()
        temp, result = self.get_temp(), self.get_temp()

        self.insert_instruction(Operation.Mult, idx, "#4", temp)
        self.insert_instruction(Operation.Assign, str(arr_id), result)
        self.insert_instruction(Operation.Add, result, temp, result)

        self.semantic_stack.push(f"@{result}")

    def save(self, token):
        self.semantic_stack.push(self.index)
        self.index += 1

    def label(self, token):
        self.semantic_stack.push(self.index)

    def jmp(self, token):
        dest = self.semantic_stack.pop()
        self.insert_instruction(Operation.Jp, str(dest))

    def clean_up(self, token):
        self.semantic_stack.pop()

    def until(self, token):
        operand1, operand2 = self.semantic_stack.pop(), self.semantic_stack.pop()
        self.insert_instruction(Operation.Jpf, operand1, operand2)

    def jpf_save(self, token):
        dest = self.semantic_stack.pop()
        src = self.semantic_stack.pop()
        self.program_block[dest] = Instruction(
            Operation.Jpf, src, str(self.index + 1), ""
        )
        self.semantic_stack.push(self.index)
        self.index += 1

    def output(self, token):
        if self.semantic_stack.top(1) == "output":
            self.insert_instruction(Operation.Print, self.semantic_stack.pop())

    # TODO: break
    def break_loop(self, token):
        self.break_stack.append(self.index)
        self.index += 1
        # TODO: break check

    def start_params(self, token):
        func_attr = self.semantic_stack.pop()
        self.semantic_stack.push(self.index)
        self.index += 1
        self.semantic_stack.push(func_attr)
        self.scanner.SYMBOL_TABLE["id"].append(SymbolTableEntry("Args ->", "", "", self.current_scope))

    def find_args_start(self):
        for i, entry in enumerate(self.scanner.SYMBOL_TABLE["id"]):
            if entry.id == "Args ->":
                return i
        return -1

    def create_record(self, token):
        return_address = self.semantic_stack.pop()

    def func_call(self, token):
        if self.semantic_stack.top() != "output":
            ...

    # TODO: Semantic checks
