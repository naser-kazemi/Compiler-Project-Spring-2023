from utils import *


# token class
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
        self.init_scanners()
        self.input_file = input_file
        self.line = None

        self.line_num = 1
        self.curser = 0

    def init_scanners(self):
        self.SYMBOL_TABLE = OrderedDict()
        self.SYMBOL_TABLE['keyword'] = ['if', 'else', 'void',
                                        'int', 'repeat', 'break', 'until', 'return']
        self.SYMBOL_TABLE['id'] = []
        self.LEXICAL_ERRORS = OrderedDict()

    def get_type_from_table(self, token):
        if token.value in self.SYMBOL_TABLE['keyword']:
            return TokenType.KEYWORD
        return TokenType.ID

    def add_lexical_error(self, token, error):
        if token.line_num not in self.LEXICAL_ERRORS:
            self.LEXICAL_ERRORS[token.line_num] = []
        self.LEXICAL_ERRORS[token.line_num].append(error)

    def read_input(self):
        with open(self.input_file, 'r') as f:
            self.lines = ''.join([line for line in f.readlines()])

    def get_current_char(self):
        return self.line[self.curser]

    def get_symbol_token(self, char):
        # lookahead for = and ==
        if char == '=':
            if self.curser + 1 < len(self.line) and self.line[self.curser + 1] == '=':
                self.curser += 1
                return Token(TokenType.SYMBOL, '==', self.line_num)
        # handle the unmatched comment
        if char == '*' and self.curser + 1 < len(self.line) and self.line[self.curser + 1] == '/':
            self.curser += 1
            return Token(TokenType.UNMATCHED_COMMENT, '*/', self.line_num)
        return Token(TokenType.SYMBOL, char, self.line_num)

    def get_num_token(self):
        num = self.get_current_char()
        while self.curser + 1 < len(self.line):
            self.curser += 1
            char = self.get_current_char()
            token_type = get_token_type(char)

            # check for the next char, if it is a symbol or whitespace, then return the token
            if token_type == TokenType.NUM:
                num += char
            elif token_type == TokenType.WHITESPACE or token_type == TokenType.SYMBOL:
                return Token(TokenType.NUM, num, self.line_num), False
            else:  # if it is invalid, then return the token and add the error
                num += char
                self.curser += 1
                return Token(TokenType.INVALID, num, self.line_num), True

        self.curser += 1
        return Token(TokenType.NUM, num, self.line_num), False

    def get_id_or_keyword_token(self):
        id_or_keyword = self.get_current_char()
        while self.curser + 1 < len(self.line):
            self.curser += 1
            char = self.get_current_char()
            token_type = get_token_type(char)

            # check for the next char, if it is a symbol or whitespace, then return the token
            if token_type == TokenType.ID or token_type == TokenType.NUM:
                id_or_keyword += char
            elif token_type == TokenType.WHITESPACE or token_type == TokenType.SYMBOL:
                return Token(TokenType.IDorKEYWORD, id_or_keyword, self.line_num), False
            else:
                id_or_keyword += char
                self.curser += 1
                return Token(TokenType.INVALID, id_or_keyword, self.line_num), True

        self.curser += 1
        return Token(TokenType.IDorKEYWORD, id_or_keyword, self.line_num), False

    def validate_comment_start(self):
        comment = self.get_current_char()
        if self.curser + 1 >= len(self.line):
            return Token(TokenType.COMMENT, comment, self.line_num), True
        self.curser += 1
        char = self.get_current_char()
        if char != '*':
            return Token(TokenType.COMMENT, comment, self.line_num), True
        comment += char
        return comment, False

    def get_comment_token(self, comment):
        while self.curser + 1 < len(self.line):
            self.curser += 1
            char = self.get_current_char()
            comment += char
            if char == '*' and self.line[self.curser + 1] == '/':
                comment += self.line[self.curser + 1]
                self.curser += 1
                return Token(TokenType.COMMENT, comment, self.line_num), False

        self.curser += 1
        return Token(TokenType.COMMENT, comment, self.line_num), True

    def get_next_token(self):
        current_char = self.get_current_char()
        token_type = get_token_type(current_char)

        # if the token is a whitespace, then skip it and get the next token
        if token_type == TokenType.WHITESPACE:
            self.curser += 1
            if current_char == '\n':  # if the char is a new line, then increment the line number
                self.line_num += 1
            return self.get_next_token()

        if token_type == TokenType.SYMBOL:
            token = self.get_symbol_token(current_char)
            if token.type == TokenType.UNMATCHED_COMMENT:
                return self.add_lexical_error(token, (token.value, 'Unmatched comment'))
            return token

        if token_type == TokenType.NUM:
            token, is_invalid = self.get_num_token()
            if not is_invalid:
                return token
            self.add_lexical_error(token, (token.value, 'Invalid number'))

        if token_type == TokenType.IDorKEYWORD:
            token, is_invalid = self.get_id_token()
            if not is_invalid:
                name, token_type, line_num = token.value, self.get_type_from_table(
                    token), token.line_num
                self.symbol_table['id'].append((name, line_num))
                return Token(token_type, name, line_num)
            self.add_lexical_error(token, (token.value, 'Invalid input'))

        if token_type == TokenType.COMMENT:
            comment, is_invalid = self.validate_comment_start()
            if not is_invalid:
                token, is_not_closed = self.get_comment_token(comment)
                if not is_not_closed:
                    return token
                self.add_lexical_error(
                    token, (token.value, 'Unclosed comment'))
            self.add_lexical_error(
                Token(TokenType.COMMENT, comment, self.line_num), (comment, 'Unmatched comment'))

    def is_eof(self):
        return self.curser >= len(self.lines)


if __name__ == '__main__':
    pass
