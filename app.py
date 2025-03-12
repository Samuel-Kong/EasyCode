import streamlit as st
import re
import sys
import io

# Token specification for the language
tokens = [
    ('SET', r'\bset\b'),
    ('SHOW', r'\bshow\b'),
    ('TO', r'\bto\b'),
    ('NUMBER', r'\d+'),
    ('VARIABLE', r'[a-zA-Z_][a-zA-Z_0-9]*'),
    ('STRING', r'"[^"]*"'),
    ('WHITESPACE', r'\s+'),
    ('MISMATCH', r'.')
]

def tokenize(code):
    """Tokenizes the input code into meaningful components."""
    code = code.strip()
    token_specification = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in tokens)
    token_regex = re.compile(token_specification)
    token_list = []
    
    # Match tokens and store them, ignoring whitespace
    for match in re.finditer(token_regex, code):
        kind = match.lastgroup
        value = match.group()
        if kind != 'WHITESPACE':
            token_list.append((kind, value))
    
    return token_list

# Abstract Syntax Tree Node
class ASTNode:
    def __init__(self, type, value=None):
        self.type = type
        if isinstance(value, tuple):
            self.value = value  # Store the tuple (variable, value) as the node's value
        else:
            self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

# Parsing function to create an Abstract Syntax Tree (AST)
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
                        # Return an AST node with the variable and value as a tuple
                        return ASTNode('set', (var_token[1], expr_token[1]))
        return None

    # Start by trying to parse a 'set' command
    node = parse_set()
    if node:
        return node
    return None

# Function to generate Python code from AST
def generate_code(ast):
    if ast.type == 'set':
        var = ast.value[0]  # Variable is the first element in the tuple
        value = ast.value[1]  # Value is the second element in the tuple
        return f'{var} = {value}'

# Function to execute the generated Python code in a specific context
def execute_code(code):
    context = {}
    try:
        exec(code, context)  # Execute code in the provided context
        return context  # Return the context to fetch variable values
    except Exception as e:
        return f"Execution failed: {e}"



def run_code(input_code):
    # Save the current stdout so we can capture the output
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        # Run the code entered by the user
        exec(input_code)

        # Capture the result (only the actual relevant output)
        output = sys.stdout.getvalue()
    except Exception as e:
        output = f"Error: {e}"

    # Reset stdout to the original
    sys.stdout = old_stdout

    # Return the captured output or any error messages
    return output.strip()

# Streamlit UI
st.title('Simplified Language Interpreter')

# Input box for user to write code
input_code = st.text_area("Enter your code here:")

# Button to execute the code
if st.button("Run Code"):
    generated_code, execution_result = run_code(input_code)
    
    # Show the output (generated Python code)
    st.subheader("Generated Python Code:")
    st.code(generated_code)
    
    # Show the execution result (values in the context)
    if execution_result:
        st.subheader("Execution Result:")
        if isinstance(execution_result, dict):
            for var, value in execution_result.items():
                st.write(f'{var} = {value}')  # Show variables in the context
        else:
            st.error(execution_result)
