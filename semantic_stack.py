from utils import *


class StackEntry:
    def __init__(self, value, description):
        self.value = value
        self.description = description

    def __repr__(self):
        if self.description == "":
            return f"{self.value}"
        return f"{self.value} ({self.description})"

    def __str__(self):
        return self.__repr__()


class SemanticStack:
    def __init__(self):
        self.stack = []

    def push(self, item, description=""):
        self.stack.append(StackEntry(item, description))

    def pop(self, count=1):
        if count != 1:
            entries = []
            for _ in range(count):
                entries.append(self.stack.pop().value)
            return tuple(entries)
        entry = self.stack.pop()
        if entry.description:
            return entry.value, entry.description
        return entry.value

    def top(self, offset=0, description=False):
        entry = self.stack[-1 - offset]
        if description:
            return entry.value, entry.description
        return entry.value

    @property
    def size(self):
        return len(self.stack)

    def empty(self):
        return self.size == 0

    def __repr__(self):
        return str(self.stack)

    def __str__(self):
        return self.__repr__()


class ReturnStackEntry:
    def __init__(self, func_id, index, value):
        self.func_id = func_id
        self.index = index
        self.value = value

    @staticmethod
    def return_instance(func_id):
        index = -1
        value = RETURN
        return ReturnStackEntry(func_id, index, value)

    def is_return(self):
        return self.index == -1 and self.value == RETURN

    def __repr__(self):
        return f"{self.func_id} {self.index} {self.value}"

    def __str__(self):
        return self.__repr__()


class ReturnStack:
    def __init__(self):
        self.stack = []
        self.last_return_index = -1

    def push(self, func_id, index, value):
        self.stack.append(ReturnStackEntry(func_id, index, value))

    def push_return(self, func_id):
        self.stack.append(ReturnStackEntry.return_instance(func_id))

    def pop(self):
        return self.stack.pop()

    def top(self, offset=0):
        return self.stack[-1 - offset]

    def last_return(self):
        idx = len(self.stack) - 1
        while idx >= 0:
            if self.stack[idx].is_return():
                self.last_return_index = idx
                return self.stack[idx], idx
            idx -= 1
        return None, None

    def empty(self):
        return len(self.stack) == 0

    def __setitem__(self, key, value):
        self.stack[key] = value

    def __getitem__(self, key):
        return self.stack[key]

    def __repr__(self):
        return str(self.stack)

    def __str__(self):
        return self.__repr__()

    def remove_last_func(self):
        self.stack = self.stack[: self.last_return_index]
