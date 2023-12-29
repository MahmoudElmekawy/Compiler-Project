import tkinter as tk
from tkinter import scrolledtext
from tabulate import tabulate
import tkinter.messagebox


def show_error_dialog(title, message):
    tkinter.messagebox.showerror(title, message)

class Token:
    def __init__(self, token_type, value=None, line=None):
        self.type = token_type
        self.value = value
        self.line = line

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.position = 0
        self.current_char = self.source_code[self.position]
        self.symbol_table = {}

    def advance(self):
        self.position += 1
        if self.position < len(self.source_code):
            self.current_char = self.source_code[self.position]
        else:
            self.current_char = None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            if self.current_char == '\n':
                self.line += 1
            self.advance()

    def get_identifier(self):
        result = ""
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result

    def get_number(self):
        result = ""
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()
        return result

    def get_string_literal(self, quote):
        result = quote
        self.advance()  
        while self.current_char and self.current_char != quote:
            result += self.current_char
            self.advance()
        result += quote
        self.advance()  
        return result

   
    def get_operator(self, operators, punctuators):
        result = ""
        while self.current_char and (self.current_char in operators or self.current_char in punctuators):
            result += self.current_char
            self.advance()

       
        if result in operators or result in punctuators:
            return result
        else:
           
            return result[:-1]


    def analyze(self):
        tokens = []
        self.line = 1

        current_data_type = None

        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
            elif self.current_char.isalpha() or self.current_char == '_':
                identifier = self.get_identifier()
                if identifier in ['int', 'float', 'char']:
                    current_data_type = identifier
                else:
                    tokens.append(Token('IDENTIFIER', identifier, self.line))
                    if identifier not in self.symbol_table:
                        self.symbol_table[identifier] = {'data_type': current_data_type, 'line': self.line}
            elif self.current_char.isdigit() or self.current_char == '.':
                number = self.get_number()
                if '.' in number:
                    tokens.append(Token('FLOAT', float(number), self.line))
                else:
                    tokens.append(Token('INTEGER', int(number), self.line))
            elif self.current_char in ['"', "'"]:
                string_literal = self.get_string_literal(self.current_char)
                tokens.append(Token('LITERAL', string_literal, self.line))
            else:
                operators = ['+', '-', '*', '/', '=']
                punctuators = [';', ',', "'", '"']
                operator = self.get_operator(operators, punctuators)
                if operator:
                    if operator in operators:
                        tokens.append(Token('OPERATOR', operator, self.line))
                    elif operator in punctuators:
                        tokens.append(Token('PUNCTUATOR', operator, self.line))
                else:
            
                    self.advance()

        return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index]

    def advance(self):
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = None

    def match(self, expected_type):
        if self.current_token and self.current_token.type == expected_type:
            token = self.current_token
            self.advance()
            return token
        else:
            show_error_dialog("Error", f"Expected {expected_type} but found {self.current_token.type} at line {self.current_token.line}")
            raise SyntaxError(f"Expected {expected_type} but found {self.current_token.type} at line {self.current_token.line}")

    def program(self):
        while self.current_token:
            try:
                self.statement()
            except SyntaxError as e:
                print(f"SyntaxError: {e}")
                self.synchronize()

    def statement(self):
        try:
            if self.current_token.type == 'IDENTIFIER':
                self.assignment_statement()
            else:
                show_error_dialog("Error", f"Unexpected token {self.current_token.type} at line {self.current_token.line}")
                raise SyntaxError(f"Unexpected token {self.current_token.type} at line {self.current_token.line}")
        except SyntaxError as e:
            print(f"SyntaxError: {e}")
            self.synchronize()

    def synchronize(self):
       
        while self.current_token and self.current_token.type != 'PUNCTUATOR':
            self.advance()

       
        if self.current_token and self.current_token.type == 'PUNCTUATOR' and self.current_token.value == ';':
            self.match('PUNCTUATOR')
    
    def assignment_statement(self):
        identifier_token = self.match('IDENTIFIER')
        self.match('OPERATOR') 
        expression_token = self.expression()
       
       
        if self.current_token and self.current_token.type == 'PUNCTUATOR' and self.current_token.value == ';':
            self.match('PUNCTUATOR')  
        else:
           
          show_error_dialog("Error", f"Missing semicolon after {identifier_token.value} = {expression_token.value}. Expected ';' at line {identifier_token.line}")
          raise  SyntaxError(f"Error: Missing semicolon after {identifier_token.value} = {expression_token.value}. Expected ';' at line {identifier_token.line}")
        
    def expression(self):
        if self.current_token.type in ['INTEGER', 'FLOAT', 'LITERAL']:
            return self.match(self.current_token.type)
        else:
            show_error_dialog("Error", f"Unexpected token {self.current_token.type} at line {self.current_token.line}")
            raise SyntaxError(f"Unexpected token {self.current_token.type} at line {self.current_token.line}")


class CompilerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Basic Compiler")
        
        self.input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=10)
        self.input_text.pack(padx=10, pady=10)

        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=10, state=tk.DISABLED)
        self.output_text.pack(padx=10, pady=10)

        self.run_button = tk.Button(root, text="Run Compiler", command=self.run_compiler)
        self.run_button.pack(pady=10)

    def display_output(self, text, color="black"):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.tag_add("color", "1.0", tk.END)
        self.output_text.tag_config("color", foreground=color)
        self.output_text.config(state=tk.DISABLED)

    def run_compiler(self):
        source_code = self.input_text.get("1.0", tk.END)
        lexer = Lexer(source_code)
        try:
            tokens = lexer.analyze()
            parser = Parser(tokens)
            parser.program()
            lexer = Lexer(source_code)
            tokens = lexer.analyze()
            tokens_list = [(token.type, token.value, token.line) for token in tokens]
            symbol_table_list = [(identifier, data['data_type'], data['line']) for identifier, data in lexer.symbol_table.items()]
          
            self.display_output(tabulate(tokens_list, headers=['Token Type', 'Value', 'Line'], tablefmt="fancy_grid") + '\n' +tabulate(symbol_table_list, headers=['Identifier', 'Data Type', 'Line'], tablefmt="fancy_grid"), color="black")

        except SyntaxError as e:
           
            error_message = f"Syntax Error: {e}"
            self.display_output(error_message, color="red")
            print(error_message)
    
    def show_error_dialog(self, title, message):
        tk.messagebox.showerror(title, message)

if __name__ == "__main__":
    root = tk.Tk()
    compiler_ui = CompilerUI(root)
    root.mainloop()
