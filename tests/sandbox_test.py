from nicegui import ui
from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins

# Safe built-ins for the sandbox
safe_builtins['_print_'] = print  # Allow the use of `print`
safe_builtins['__import__'] = __import__  # Allow importing modules (with caution)

def execute_code(code: str):
    """Execute user-provided code in a restricted environment."""
    try:
        # Compile the code with RestrictedPython
        byte_code = compile_restricted(code, '<string>', 'exec')
        
        # Create a restricted execution environment
        restricted_globals = {
            '__builtins__': safe_builtins,
            '_print_': print,  # Allow `print` function
        }
        restricted_locals = {}
        
        # Execute the code
        exec(byte_code, restricted_globals, restricted_locals)
        
        # Capture the output (if any)
        output = restricted_locals.get('_print_', 'No output')
        return f"Execution successful!\nOutput: {output}"
    except Exception as e:
        return f"Error: {str(e)}"

@ui.page('/')
def sandbox_page():
    ui.label('Dynamic Code Execution').classes('text-xl')
    
    # Text area for code input
    code_input = ui.textarea(label='Enter your Python code here').classes('w-full')
    
    # Button to execute the code
    ui.button('Run Code', on_click=lambda: output.set_text(execute_code(code_input.value)))
    
    # Display the output
    output = ui.label().classes('text-green-500')

ui.run()