from nicegui import events, ui
import asyncio
import os
import httpx
import websockets

BACKEND_WS_URL = "ws://localhost:8000/process-pdf"
dynamic_container = ui.row().classes("w-full")

def execute_generated_code(code: str):
    """Execute generated code in the dynamic container"""
    dynamic_container.clear()
    exec_globals = {
        'ui': ui,
        'dynamic_container': dynamic_container,
        'os': os
    }
    
    try:
        with dynamic_container:
            exec(code, exec_globals)
        ui.notify("Code executed successfully!", type='positive')
    except Exception as e:
        ui.notify(f"Execution error: {str(e)}", type='negative')

def handle_upload(e: events.UploadEventArguments):
    global file_content
    file_content = e.content.read()
    global file_name
    file_name = e.name

async def process_pdf():
    spinner = None
    try:
        # Check if files were uploaded
        if not file_content:
            output_label.set_text("Error: Please upload a PDF file first.")
            return

        # Show spinner while processing
        spinner = ui.spinner(size='lg')
        spinner.visible = True

        async with websockets.connect(BACKEND_WS_URL) as websocket:
            # Send the file and filename
            await websocket.send(file_content)
            await websocket.send(file_name)

            # Receive progress updates
            while True:
                message = await websocket.recv()
                print(message)
                if isinstance(message, dict):  # Final result
                    result = message
                    break
    
                output_label.set_text(message)

            # Execute the generated code
            execute_generated_code(result['generated_code'])
            output_label.set_text(
                f"Web App Description:\n{result['spec_doc']}\n\nGenerated Code:\n{result['generated_code']}"
            )

    except Exception as e:
        output_label.set_text(f"Error: {str(e)}")
        ui.notify(f"Processing error: {str(e)}", type='negative')
    finally:
        if spinner:
            spinner.visible = False

@ui.page('/')
def main():
    ui.label("PDF to Web App Generator").classes("text-xl font-bold")
    
    global file_upload
    file_upload = ui.upload(label="Upload PDF", on_upload=handle_upload).classes("w-full")
    
    global output_label
    output_label = ui.label().classes("text-green-500 whitespace-pre-wrap")
    
    ui.button("Generate Code", on_click=process_pdf).classes("mt-4")
    dynamic_container.classes("w-full p-4 border-2 rounded-lg mt-4")

ui.run()