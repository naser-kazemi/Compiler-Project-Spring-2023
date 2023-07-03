from utils import *
from pb import Instruction, ProgramBlock
from semantic_stack import StackEntry, SemanticStack
from semantic_error_logger import SemanticErrorLogger
from scanner import Scanner, Token, SymbolTableEntry, FunctionRecordEntry


class CodeGenerator:
    def __init__(self, scanner):
        self.semantic_stack = SemanticStack()
        self.program_block = ProgramBlock()
        self.scanner = scanner
        self.error_logger = SemanticErrorLogger(self.scanner)
        self.break_stack = []
        self.return_stack = []
        self.index = 0
        self.current_scope = 0
        self.temp_address = 500
        self.token = None

    def call_routine(self, name, token):
        # print(f"Calling {name} routine")
        # print(self.semantic_stack)
        # print(self.scanner.SYMBOL_TABLE["id"])
        name = name.replace("#", "")
        routine = self.__getattribute__(name)
        if routine.__code__.co_argcount == 2:
            routine(token)
        else:
            routine()

    def insert_instruction(self, opcode, operand1, operand2="", operand3=""):
        instruction = Instruction(opcode, operand1, operand2, operand3)
        # print(instruction)
        self.program_block.append(instruction)
        self.index += 1

    def add_index(self, num=1):
        for _ in range(num):
            self.program_block.append(Instruction.empty())
        self.index += num

    def find_address(self, item):
        if item == "output":
            return item
        for record in self.scanner.SYMBOL_TABLE["id"][::-1]:
            if record.id == item:
                if isinstance(record, FunctionRecordEntry):
                    return record
                return record.address

    def get_temp(self, count=1):
        for _ in range(count):
            self.insert_instruction(Operation.Assign, "#0", str(self.temp_address))
            self.temp_address += 4
        return str(self.temp_address - 4 * count)

    def def_var(self):
        var_id = self.semantic_stack.pop()
        # TODO: void check
        self.error_logger.void_check(self.token, var_id)
        address = self.get_temp()
        self.scanner.SYMBOL_TABLE["id"].append(
            SymbolTableEntry(var_id, "int", address, self.current_scope)
        )
        # print("def_var")
        # print(self.scanner.SYMBOL_TABLE["id"])

    def def_arr(self):
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
        # print("def_arr")
        # print(self.scanner.SYMBOL_TABLE["id"])

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
        # print(f"save_opr: {address}")
        self.semantic_stack.push(address)

    def assign_opr(self, token):
        # print(self.semantic_stack.stack)
        operand1, operand2 = self.semantic_stack.top(), self.semantic_stack.top(1)
        # print(self.scanner.SYMBOL_TABLE["id"])
        # print(operand1, operand2)
        # operand1, operand2 = self.semantic_stack.pop(), self.semantic_stack.pop()
        self.error_logger.type_mismatch(token, operand2, operand1)
        self.insert_instruction(Operation.Assign, operand1, operand2)
        self.semantic_stack.pop()

    def mult(self, token):
        result = self.get_temp()
        operand2, operand1 = self.semantic_stack.pop(), self.semantic_stack.pop()
        self.error_logger.type_mismatch(token, operand1, operand2, mult=True)
        self.insert_instruction(Operation.Mult, operand1, operand2, result)
        # print(f"mult: {result}")
        self.semantic_stack.push(result)

    def def_arr_arg(self):
        temp = self.scanner.SYMBOL_TABLE["id"].pop()
        self.scanner.SYMBOL_TABLE["id"].append(
            SymbolTableEntry(temp.id, "int*", temp.address, temp.scope)
        )
        # print("def_arr_arg")
        # print(self.scanner.SYMBOL_TABLE["id"])

    def arr_idx(self):
        idx, arr_addr = self.semantic_stack.pop(), self.semantic_stack.pop()
        temp, result = self.get_temp(), self.get_temp()

        self.insert_instruction(Operation.Mult, "#4", idx, temp)
        self.insert_instruction(Operation.Assign, str(arr_addr), result)
        self.insert_instruction(Operation.Add, result, temp, result)

        self.semantic_stack.push(f"@{result}")

    def save(self):
        self.semantic_stack.push(self.index)
        self.add_index()

    def label(self):
        self.semantic_stack.push(self.index)

    def jmp(self):
        dest = self.semantic_stack.pop()
        self.program_block[int(dest)] = Instruction(Operation.Jp, str(self.index), "", "")

    def clean_up(self):
        self.semantic_stack.pop()

    def new_break(self):
        self.break_stack.append("BREAK")

    def until(self):
        operand1, operand2 = self.semantic_stack.pop(), self.semantic_stack.pop()
        self.insert_instruction(Operation.Jpf, operand1, operand2)
        # operand1, operand2 = self.semantic_stack.top(), self.semantic_stack.top(1)
        # self.insert_instruction(Operation.Jpf, operand1, operand2)
        # self.semantic_stack.pop()

    def end_break(self):
        # print("end_break")
        last_block = last_index_of(self.break_stack, "BREAK")
        for record in self.break_stack[last_block + 1:]:
            self.program_block[record] = Instruction(Operation.Jp, str(self.index), "", "")
        self.break_stack = self.break_stack[:last_block]
        # print(self.break_stack)

    def jpf_save(self):
        dest = self.semantic_stack.pop()
        src = self.semantic_stack.pop()
        # print(dest)
        # print(len(self.program_block.instructions))
        self.program_block[dest] = Instruction(
            Operation.Jpf, src, str(self.index + 1), ""
        )
        self.semantic_stack.push(self.index)
        self.add_index()

    def output(self):
        if self.semantic_stack.top(1) == "output":
            self.insert_instruction(Operation.Print, self.semantic_stack.pop())

    # TODO: break
    def break_loop(self, token):
        # print("break_loop")
        # print(self.break_stack)
        self.break_stack.append(self.index)
        self.add_index()
        # TODO: break check
        self.error_logger.break_check(self.break_stack, token)
        # print(token.line_num, token.value)

    def start_params(self):
        func_attr = self.semantic_stack.pop()
        self.semantic_stack.push(self.index)
        self.add_index()
        self.semantic_stack.push(func_attr)
        self.scanner.SYMBOL_TABLE["id"].append(
            SymbolTableEntry("Args ->", "", "", self.current_scope)
        )

    def find_args_start(self):
        for i, entry in enumerate(self.scanner.SYMBOL_TABLE["id"]):
            if entry.id == "Args ->":
                return i
        return -1

    def create_record(self):
        return_address = self.get_temp()
        index = self.index
        return_value = self.get_temp()
        self.semantic_stack.push(return_value)
        self.semantic_stack.push(return_address)
        func_id = self.semantic_stack.top(2)
        args_start = self.find_args_start()
        function_record = FunctionRecordEntry(
            return_address,
            return_value,
            func_id,
            index,
            self.scanner.SYMBOL_TABLE["id"],
            args_start,
            self.current_scope,
        )
        # print(function_record)
        self.scanner.SYMBOL_TABLE["id"].pop(args_start)
        self.scanner.SYMBOL_TABLE["id"].append(function_record)

    def end_func(self):
        self.semantic_stack.pop(3)
        dest = self.semantic_stack.pop()
        address = self.get_temp()
        for record in self.scanner.SYMBOL_TABLE["id"][::-1]:
            if isinstance(record, FunctionRecordEntry):
                if record.id == "main":
                    self.program_block[dest] = Instruction(Operation.Assign, "#0", address, "")
                    return
                break
        self.program_block[dest] = Instruction(Operation.Jp, str(self.index), "", "")

    def func_call(self, token):
        if self.semantic_stack.top() == "output":
            return
        args = []
        record = None
        while not (self.semantic_stack.empty() or isinstance(record, FunctionRecordEntry)):
            record = self.semantic_stack.pop()
            args.append(record)
        function_record = args.pop() if isinstance(record,
                                                   FunctionRecordEntry) else FunctionRecordEntry.empty_instance()
        args = args[::-1]
        self.error_logger.parameter_num_matching(token, args, function_record)

        func_args = function_record.args
        # print(func_args)
        # print(args)
        for i, (var, arg) in enumerate(zip(func_args, args)):
            self.error_logger.parameter_type_matching(token, var, arg, i + 1)
            self.insert_instruction(Operation.Assign, arg, var.address)

        self.insert_instruction(
            Operation.Assign, f"#{self.index + 2}", function_record.return_address
        )
        self.insert_instruction(Operation.Jp, function_record.index)
        result = self.get_temp()
        self.insert_instruction(Operation.Assign, function_record.return_value, result)
        self.semantic_stack.push(result)

    def save_return(self):
        self.return_stack.append((self.index, self.semantic_stack.pop()))
        self.add_index(2)

    def push_scope(self):
        self.current_scope += 1

    def pop_scope(self):
        symbol_table = self.scanner.SYMBOL_TABLE["id"].copy()
        for record in symbol_table[::-1]:
            # print(record)
            if record.scope == self.current_scope:
                # print(record)
                self.scanner.SYMBOL_TABLE["id"].pop()
        self.current_scope -= 1

    def push_idx(self):
        self.semantic_stack.push(self.index)

    # TODO: Semantic checks
