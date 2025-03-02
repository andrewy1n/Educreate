import json
from nicegui import events, ui
import asyncio
import os
import httpx
import websockets
import textwrap

BACKEND_WS_URL = "ws://localhost:8000/process-pdf"
dynamic_container = ui.row().classes("w-full")

dynamic_container.classes("w-full min-h-[400px] border-2 rounded-lg")
ui.query('.nicegui-content').classes('w-full h-full')

# Initialize global variables for file handling
file_content = None
file_name = None

def execute_generated_code(code: str):
    """Execute generated code in the dynamic container"""
    dynamic_container.clear()
    exec_globals = {
        'ui': ui,
        'dynamic_container': dynamic_container,
        'os': os,
        '__name__': '__main__'
    }
    
    try:
        code = code.replace("ui.run()", "")
        
        exec(code, exec_globals)
            
        ui.update()
        
    except Exception as e:
        ui.notify(f"Execution error: {str(e)}", type='negative')
        print("Problematic code:\n", code)

def handle_upload(e: events.UploadEventArguments):
    global file_content, file_name
    file_content = e.content.read()
    file_name = e.name
    ui.notify(f"Uploaded {file_name}")

async def process_pdf():
    spinner = None
    status_label = None
    llm_log = None  # Initialize LLM log box
    code_block = None  # Initialize code block UI

    try:
        if not file_content:
            output_label.set_text("Error: Please upload a PDF file first.")
            return

        # Show spinner and status label
        spinner = ui.spinner(size='lg')
        spinner.visible = True
        status_label = ui.label("Connecting to server...").classes("text-sm text-gray-600")

        # Create a log box for LLM messages
        llm_log = ui.textarea(label="LLM Messages").classes("w-full").style("height: 40%;").props("readonly")

        # Create a code block UI for displaying code
        code_block = ui.code().classes("w-full bg-gray-100 p-4 rounded-lg").style("height: 40%; white-space: pre-wrap;")
        code_block.visible = False  # Hide initially

        async with websockets.connect(
            BACKEND_WS_URL,
            ping_interval=60,
            ping_timeout=600,
        ) as websocket:
            # Update status
            status_label.set_text("Sending file to server...")
            await websocket.send(file_content)
            await websocket.send(file_name)

            # Receive progress updates
            while True:
                message = await websocket.recv()
                print("Received:", message)

                try:
                    # Attempt to parse JSON
                    result = json.loads(message)
                    if isinstance(result, dict):  # Final result
                        if result['type'] == "generated_code":
                            status_label.set_text("Generating UI...")
                            execute_generated_code(textwrap.dedent(result['generated_code']))
                            ui.notify("Generation complete!", type='positive')
                            status_label.set_text("Done!")  # Final status
                            break
                        elif result['type'] == "llm_message":
                            llm_log.value += f"{result['message']}"
                            llm_log.update()  # Force UI update
                        elif result['type'] == "llm_message_done":
                            print("message finished")
                            llm_log.value = ""
                            code_block.visible = False
                            llm_log.update()
                        elif result['type'] == "llm_code_message":
                            code_block.set_text(result['message'])
                            code_block.visible = True
                            code_block.update()
                    else:
                        status_label.set_text(result['message'])
                        ui.update()
                except json.JSONDecodeError:
                    # If not JSON, treat as text and update status
                    status_label.set_text(message)

    except Exception as e:
        output_label.set_text(f"Error: {str(e)}")
        ui.notify(f"Processing error: {str(e)}", type='negative')
        if status_label:
            status_label.set_text(f"Error: {str(e)}")
    finally:
        if spinner:
            spinner.visible = False

async def mock_process_pdf():
    spinner = None
    try:
        spinner = ui.spinner(size='lg')
        spinner.visible = True

        generated_code = textwrap.dedent("""
            from nicegui import ui
            
            with ui.card().classes('w-full p-4'):
                ui.label('Dynamic Content').classes('text-h4')
                ui.button('Test Button', on_click=lambda: ui.notify('Works!'))
        """)

        execute_generated_code(generated_code)
        await asyncio.sleep(0.1)  # Allow event loop to process changes

    except Exception as e:
        output_label.set_text(f"Error: {str(e)}")
        ui.notify(f"Processing error: {str(e)}", type='negative')
    finally:
        if spinner:
            spinner.visible = False

@ui.page('/')
def main():
    ui.label("PDF to Web App Generator").classes("text-xl font-bold")
    
    global file_upload, output_label
    file_upload = ui.upload(label="Upload PDF", on_upload=handle_upload).classes("w-full")
    output_label = ui.label().classes("text-green-500 whitespace-pre-wrap")
    
    ui.button("Generate Code", on_click=process_pdf).classes("mt-4")
    dynamic_container.classes("w-full p-4 border-2 rounded-lg mt-4")

ui.run()