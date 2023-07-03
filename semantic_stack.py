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
