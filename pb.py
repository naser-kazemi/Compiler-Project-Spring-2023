from utils import *
from typing import List, OrderedDict, Union


class Instruction:
    def __init__(self, operation: Operation, arg1: str, arg2: str, result: str):
        self.operation = operation
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result

    @staticmethod
    def empty():
        return Instruction(Operation.Empty, "", "", "")

    def __repr__(self) -> str:
        return (
            f"{self.operation.value} {self.arg1} {self.arg2} {self.result}"
            if self.operation != Operation.Empty
            else ""
        )


class ProgramBlock:
    def __init__(self):
        self.instructions = []

    @property
    def i(self):
        return len(self.instructions)

    @i.setter
    def i(self, value):
        if value < self.i:
            self.instructions = self.instructions[:value]
        else:
            self.instructions.extend(
                [Instruction.empty() for _ in range(value - self.i)]
            )

    def append(self, instruction: Instruction):
        self.instructions.append(instruction)

    def __setitem__(self, key, value):
        self.instructions[key] = value

    def __getitem__(self, key):
        return self.instructions[key]

    def __str__(self) -> str:
        return "\n".join([f"{i}\t{inst}" for i, inst in enumerate(self.instructions)])
