import streamlit as st
import sys
import io
import re

# Function to transform the simplified code into Python code using regex
def simplify_syntax(input_code):

    # Replace 'set x to ask "question"' with 'x = input("question")'
    input_code = re.sub(r'\bset\s+(\w+)\s+to\s+ask\s+"(.*?)"', r'\1 = input("\2")', input_code)

    # Replace 'set x to y' with 'x = y' (including numbers and variables)
    input_code = re.sub(r'\bset\s+(\w+)\s+to\s+(\S+)', r'\1 = \2', input_code)
    
    # Use regex to replace 'show x' with 'print(x)'
    input_code = re.sub(r'\bshow\s+(.*)', r'print(\1)', input_code)
    
    return input_code

# Function to run the simplified code entered by the user
def run_code(input_code):
    # Simplify the input code first
    python_code = simplify_syntax(input_code)
    
    # Save the current stdout so we can capture the output
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        # Execute the simplified Python code
        exec(python_code)
        # Capture the output from the executed code
        output = sys.stdout.getvalue()
    except Exception as e:
        # Capture any exceptions (errors in the code)
        output = f"Error: {e}"

    # Reset stdout to the original
    sys.stdout = old_stdout

    # Return the captured output or error message
    return output.strip()

# Streamlit app layout
st.title("EasyCode: Simple Code Executor")

# Input for the user code (using the easier syntax)
input_code = st.text_area("Enter your code (use easy syntax):", height=200)

# Button to run the code
if st.button("Run Code"):
    # Run the simplified user code and capture the result
    execution_result = run_code(input_code)

    # Display the result of the code execution
    st.subheader("Output:")
    st.code(execution_result)
