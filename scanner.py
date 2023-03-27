from utils import *

SYMBOL_TABLE = OrderedDict()


class Token:
    def __init__(self, token_type, value, line_num):
        self.token_type = token_type
        self.value = value
        self.line_num = line_num

    def __str__(self):
        return f'({self.token_type}, {self.value})'

    def __repr__(self):
        return str(self)


class Scanner:
    def __init__(self, input_file):
        self.input_file = input_file
        self.line = None

        self.line_num = 1
        self.curser = 0

    def read_input(self):
        with open(self.input_file, 'r') as f:
            self.lines = ''.join([line for line in f.readlines()])

    def get_current_char(self):
        return self.line[self.curser]
    
    
    def get_symbol_token(self, char):
        if char == '=':
            if self.curser + 1 < len(self.line) and self.line[self.curser + 1] == '=':
                self.curser += 1
                return Token(TokenType.SYMBOL, '==', self.line_num)
        return Token(TokenType.SYMBOL, char, self.line_num)
    
    def get_num_token(self):
        num = self.get_current_char()
        while self.curser + 1 < len(self.line):
            self.curser += 1
            char = self.get_current_char()
            token_type = get_token_type(char)
            
            if token_type == TokenType.NUM:
                num += char
            elif token_type == TokenType.WHITESPACE or token_type == TokenType.SYMBOL:
                return Token(TokenType.NUM, num, self.line_num), False
            # else:
                # self
                
            
    

    def get_next_token(self):
        current_char = self.get_current_char()
        token_type = get_token_type(current_char)
        
        if token_type == TokenType.WHITESPACE:
            self.curser += 1
            if current_char == '\n':
                self.line_num += 1
            return self.get_next_token()
        
        # lookahead for = and ==
        if token_type == TokenType.SYMBOL:
            return self.get_symbol_token(current_char)
            
        if token_type == TokenType.NUM:
            return self.get_num_token(current_char)
        
        
        


    def is_eof(self):
        return self.curser >= len(self.lines)


if __name__ == '__main__':
    pass
