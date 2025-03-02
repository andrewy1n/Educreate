import asyncio
import json
from nicegui import events, ui
import os
import websockets
import textwrap
from datetime import datetime

BACKEND_WS_URL = "ws://localhost:8000/process-pdf"

# Global state
generated_code = None
generated_description = ""
generated_progress = ""
file_content = None
file_name = None

def handle_upload(e: events.UploadEventArguments):
    global file_content, file_name
    file_content = e.content.read()
    file_name = e.name
    ui.notify(f"Uploaded {file_name}")

def execute_generated_code(code: str, container: ui.column):
    container.clear()
    
    exec_globals = {
        'ui': ui,
        'container': container,
        'os': os,
        '__name__': '__main__'
    }
    
    try:
        code = code.replace("ui.run()", "")
        with container:
            exec(code, exec_globals)
        ui.update()
    except Exception as e:
        ui.notify(f"Execution error: {str(e)}", type='negative')

async def process_pdf():
    global generated_code, generated_description, generated_progress
    try:
        if not file_content:
            ui.notify("Please upload a PDF file first", type='negative')
            return

        # Initialize progress dialog
        with ui.dialog() as progress_dialog, ui.card().classes("w-full max-w-4xl p-4 gap-4"):
            ui.spinner(size='lg')
            ui.label("Generating code...").classes("text-lg")
            
            ui.label("Generation Progress").classes("text-lg mt-4")
            with ui.column().classes("w-full border rounded-lg p-4 h-64 overflow-y-auto") as log_container:
                progress_label = ui.textarea().bind_value(globals(), 'generated_progress').classes("w-full h-64").props('readonly')

        progress_dialog.open()
        
        async with websockets.connect(
            BACKEND_WS_URL,
            ping_interval=60,
            ping_timeout=600,
            ) as websocket:
            await websocket.send(file_content)
            await websocket.send(file_name)

            while True:
                message = await websocket.recv()
                print(message)
                try:
                    result = json.loads(message)
                    if result['type'] == "generated_code":
                        generated_code = textwrap.dedent(result['generated_code'])
                        generated_description = result.get('spec_doc', '')
                        execute_generated_code(generated_code, app_container)
                        ui.notify("Code generated successfully!", type='positive')
                        break
                    elif result['type'] == "llm_message":
                        generated_description += f"{result['message']}"
                except json.JSONDecodeError:
                    generated_progress += f"{message}\n"
                    ui.update(progress_label)

    except Exception as e:
        ui.notify(f"Error: {str(e)}", type='negative')
    finally:
        progress_dialog.close()

def on_suggestion(message_input: ui.input, chat_messages: ui.column):
    """Handle suggestion submission"""
    message = message_input.value
    if not message.strip():
        return
    
    # Add user message
    with chat_messages:
        with ui.row().classes("w-full justify-end"):
            with ui.card().classes("bg-blue-50 p-2 max-w-[80%]"):
                ui.label(message).classes("text-sm text-black")
                ui.label(f"User - {datetime.now().strftime('%H:%M')}").classes("text-xs text-gray-500")
    
    # Clear input
    message_input.value = ""
    
    # Mock AI response
    asyncio.create_task(mock_ai_response(chat_messages))

async def mock_ai_response(chat_messages: ui.column):
    """Simulate AI response"""
    await asyncio.sleep(1)
    
    # Add system response
    with chat_messages:
        with ui.row().classes("w-full justify-start"):
            with ui.card().classes("bg-white p-2 max-w-[80%]"):
                ui.label("Thank you for your suggestion! We'll consider this feedback for future improvements.").classes("text-sm text-black")
                ui.label(f"Assistant - {datetime.now().strftime('%H:%M')}").classes("text-xs text-gray-500")
@ui.page('/', dark=True)
def main():
    global app_container, generate_modal
    with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-4"):
        ui.label("AI Application Generator").classes("text-2xl font-bold")
        
        # Control buttons
        with ui.row().classes("w-full gap-4 justify-center"):
            ui.button("Generate Code", icon="rocket", on_click=lambda: generate_modal.open())
            ui.button("See Code Details", icon="code", on_click=lambda: code_details_modal.open())
        
        # Application preview section
        with ui.row().classes("w-full gap-4"):
            with ui.column().classes("w-2/3 border rounded-lg p-4 min-h-[400px]"):
                ui.label("Application Preview").classes("text-xl font-bold mt-4")
                app_container = ui.column().classes("w-full border rounded-lg p-4 min-h-[400px]")

            with ui.column().classes("w-[30%] p-4 rounded-lg border-2 h-[600px]"):
                ui.label("Suggestions Chat").classes("text-lg font-bold mb-4")
                
                # Chat messages container (NiceGUI UI element)
                chat_messages = ui.column().classes("flex-1 overflow-y-auto mb-4 gap-2 text-black")
                
                # Input form at bottom
                with ui.row().classes("w-full items-center gap-2"):
                    message_input = ui.input(placeholder="Type your suggestion...").classes("flex-1")
                    ui.button("Send", icon="send", on_click=lambda: on_suggestion(message_input, chat_messages))

    # Generate Code Modal
    with ui.dialog() as generate_modal, ui.card().classes("w-full max-w-4xl p-4 gap-4"):
        ui.label("Generate New Application").classes("text-xl font-bold")
        
        with ui.row().classes("w-full items-center gap-4"):
            ui.upload(label="Upload PDF", on_upload=handle_upload).classes("flex-1")
            ui.button("Process PDF", icon="start", on_click=process_pdf)

    # Code Details Modal
    with ui.dialog() as code_details_modal, ui.card().classes("w-full max-w-4xl p-4 gap-4 h-[80vh]"):
        ui.label("Generated Code Details").classes("text-xl font-bold")
        
        with ui.tabs().classes('w-full') as tabs:
            code_tab = ui.tab('Source Code')
            desc_tab = ui.tab('Description')
        
        with ui.tab_panels(tabs, value=code_tab).classes('w-full h-[70vh]'):
            with ui.tab_panel(code_tab).classes('h-full'):
                ui.code().classes("w-full h-full").bind_content(globals(), 'generated_code')
            with ui.tab_panel(desc_tab).classes('h-full'):
                ui.markdown().classes("w-full h-full overflow-y-auto").bind_content(globals(), 'generated_description')
    

ui.run(reload=False)