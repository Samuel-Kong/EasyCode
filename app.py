import streamlit as st
import re

# Token specification for the language
tokens = [
    ('SET', r'set'),
    ('SHOW', r'show'),
    ('NUMBER', r'\d+'),
    ('VARIABLE', r'[a-zA-Z_][a-zA-Z_0-9]*'),
    ('TO', r'to'),
    ('STRING', r'"[^"]*"'),
    ('WHITESPACE', r'\s+'),
    ('MISMATCH', r'.')
]

def tokenize(code):
    """Tokenizes the input code into meaningful components."""
    code = code.strip()
    token_specification = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in tokens)
    token_regex = re.compile(token_specification)
    for match in re.finditer(token_regex, code):
        kind = match.lastgroup
        value = match.group()
        if kind != 'WHITESPACE':
            yield (kind, value)

# Abstract Syntax Tree Node
class ASTNode:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

# Parsing function to create an AST
def parse(tokens):
    idx = 0
    def get_token():
        nonlocal idx
        if idx < len(tokens):
            return tokens[idx]
        return None

    def advance():
        nonlocal idx
        idx += 1

    def parse_set():
        token = get_token()
        if token and token[0] == 'SET':
            advance()  # 'set'
            var_token = get_token()
            if var_token and var_token[0] == 'VARIABLE':
                advance()  # variable
                next_token = get_token()
                if next_token and next_token[0] == 'TO':
                    advance()  # 'to'
                    expr_token = get_token()
                    if expr_token and expr_token[0] == 'NUMBER':
                        advance()  # number
                        return ASTNode('set', var_token[1], expr_token[1])
        return None

    # Start by trying to parse a 'set' command
    node = parse_set()
    if node:
        return node
    return None

# Function to generate Python code from AST
def generate_code(ast):
    if ast.type == 'set':
        var = ast.children[0].value
        value = ast.children[1].value
        return f'{var} = {value}'

# Function to execute the generated Python code
def execute_code(code):
    exec(code)  # This will execute Python code dynamically

# Main function to handle parsing and executing code
def run_code(input_code):
    # Tokenize the input
    tokens = list(tokenize(input_code))
    
    # Parse the tokens to create an Abstract Syntax Tree (AST)
    ast = parse(tokens)
    
    # If AST is generated, generate Python code and execute it
    if ast:
        generated_code = generate_code(ast)
        return generated_code
    else:
        return "Error: Unable to parse the code."

# Streamlit UI
st.title('Simplified Language Interpreter')

# Input box for user to write code
input_code = st.text_area("Enter your code here:")

# Button to execute the code
if st.button("Run Code"):
    output = run_code(input_code)
    
    # Show the output (generated Python code)
    st.subheader("Generated Python Code:")
    st.code(output)

    # Optionally, show the execution result (if valid)
    try:
        exec(output)
        st.subheader("Execution Result:")
        st.write(f"x = {x}")  # Example output, you can add more logic here
    except Exception as e:
        st.error(f"Execution failed: {e}")
