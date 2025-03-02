from nicegui import ui
import os
from IdeaAgent import IdeaAgent
from CodeAgent import CodeAgent

# Initialize agents outside the page function
idea_agent = IdeaAgent()
code_agent = CodeAgent()

# Create container for dynamic content
dynamic_container = ui.row().classes("w-full")

# Global variable to store the uploaded file path
uploaded_file_path = None

def execute_generated_code(code: str):
    """Execute generated code in the dynamic container"""
    dynamic_container.clear()
    exec_globals = {
        'ui': ui,
        'dynamic_container': dynamic_container,
        'os': os,
        'idea_agent': idea_agent,
        'code_agent': code_agent
    }
    
    try:
        with dynamic_container:
            exec(code, exec_globals)
        ui.notify("Code executed successfully!", type='positive')
    except Exception as e:
        ui.notify(f"Execution error: {str(e)}", type='negative')

def save_uploaded_file(upload_event):
    """Save the uploaded file immediately after upload"""
    global uploaded_file_path
    try:
        # Access the uploaded file from the event
        uploaded_file = upload_event.content  # This is a SpooledTemporaryFile
        file_name = upload_event.name

        # Ensure uploads directory exists
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        # Save the uploaded file
        uploaded_file_path = os.path.join(upload_dir, file_name)
        
        # Read the file content and write to disk
        with open(uploaded_file_path, "wb") as f:
            f.write(uploaded_file.read())  # Read the SpooledTemporaryFile content

        # Verify file was saved
        if not os.path.exists(uploaded_file_path):
            raise Exception("Failed to save uploaded file.")
        
        ui.notify("File uploaded and saved successfully!", type='positive')
    except Exception as e:
        ui.notify(f"File upload error: {str(e)}", type='negative')
        uploaded_file_path = None

def process_pdf():
    global uploaded_file_path
    spinner = None  # Initialize spinner variable
    try:
        if not uploaded_file_path:
            output_label.set_text("Error: Please upload a PDF file first.")
            return

        # Show spinner while processing
        spinner = ui.spinner(size='lg')
        spinner.visible = True  # Ensure spinner is visible

        # Generate web app description
        spec_doc = idea_agent.generate_web_app_description(uploaded_file_path)

        output_label.set_text(spec_doc)
        
        # Generate and execute code
        generated_code = code_agent.generate_code(spec_doc)
        output_label.set_text(f"Web App Description:\n{spec_doc}\n\nGenerated Code:\n{generated_code}")
        
        # Execute the generated code
        execute_generated_code(generated_code)

    except Exception as e:
        output_label.set_text(f"Error: {str(e)}")
        ui.notify(f"Processing error: {str(e)}", type='negative')
    finally:
        # Ensure spinner is turned off
        if spinner:
            spinner.visible = False

@ui.page('/')
def main():
    ui.label("PDF to Web App Generator").classes("text-xl font-bold")
    
    # File upload component
    global file_upload
    file_upload = ui.upload(label="Upload PDF", on_upload=save_uploaded_file).classes("w-full")
    
    # Button to generate code
    ui.button("Generate Code", on_click=process_pdf).classes("mt-4")
    
    # Output label to display results
    global output_label
    output_label = ui.label().classes("text-green-500 whitespace-pre-wrap")
    
    # Add dynamic container for generated UI
    dynamic_container.classes("w-full p-4 border-2 rounded-lg mt-4")

ui.run()