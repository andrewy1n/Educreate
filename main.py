from nicegui import ui
import matplotlib.pyplot as plt
import io
import base64

ui.add_head_html('''
    <title>EduCreate</title>
    <link rel="icon" type="image/x-icon" href="https://example.com/favicon.ico">
''')

answers = ['Neutral'] * 8

questions = [
    'I prefer to learn by seeing diagrams or illustrations.',
    'I prefer to listen to explanations or lectures.',
    'I prefer to learn by doing hands-on activities.',
    'I prefer reading textbooks or written instructions over watching a video.',
    'I find it easier to understand information when I hear it spoken aloud.',
    'I learn best when I take detailed notes while studying.',
    'I find it easier to remember information when I see it written down or in charts.',
    'I understand concepts better when I can physically interact with them.',
]

styles = [
    'visual',
    'auditory',
    'kinesthetic',
    'reading/writing',
    'auditory',
    'reading/writing',
    'visual',
    'kinesthetic'
]

agreement_points = {
    'Strongly Agree': 4,
    'Agree': 3,
    'Neutral': 2,
    'Disagree': 1,
    'Strongly Disagree': 0,
}

max_learning_style = "Mixed"

def calculate_learning_style():
    score_visual = 0
    score_auditory = 0
    score_kinesthetic = 0
    score_readingwriting = 0

    for answer, style in zip(answers, styles):
        if style == 'visual':
            score_visual += agreement_points[answer]
        elif style == 'auditory':
            score_auditory += agreement_points[answer]
        elif style == 'kinesthetic':
            score_kinesthetic += agreement_points[answer]
        elif style == 'reading/writing':
            score_readingwriting += agreement_points[answer]
    
    # Create a dictionary to map scores to styles
    style_scores = {
        'Visual': score_visual,
        'Auditory': score_auditory,
        'Kinesthetic': score_kinesthetic,
        'Reading/Writing': score_readingwriting
    }

    return style_scores

def create_pie_chart(scores):
    labels = list(scores.keys())
    sizes = list(scores.values())

    # Set dark theme for the plot
    plt.style.use('dark_background')  # Use dark theme
    plt.figure(figsize=(6, 6), facecolor='black')  # Set figure background to black

    # Create the pie chart
    wedges, texts, autotexts = plt.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        textprops={'color': 'white'}  # Set text color to white
    )

    # Set the color of the autopct text to white
    for autotext in autotexts:
        autotext.set_color('black')

    plt.axis('equal')  # Ensure the pie chart is circular

    # Save the plot to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor='black')  # Ensure the background is black
    buf.seek(0)
    plt.close()

    # Convert the plot to a base64-encoded string
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return image_base64

@ui.page('/survey', dark=True)
def survey_page():
    with ui.column().classes("w-full max-w-4xl mx-auto p-8 gap-8"):
        ui.label('How much do you agree with the following statements?').classes("text-3xl font-bold text-center mb-8")
        
        # Survey questions
        for i, (q, s) in enumerate(zip(questions, styles)):
            with ui.card().classes("w-full p-6 hover:bg-gray-800 transition-colors"):
                ui.label(q).classes("text-lg font-medium mb-4")
                with ui.row().classes("w-full justify-center gap-4"):
                    ui.radio(
                        options=['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'],
                        value='Neutral'
                    ).props('inline').on_value_change(lambda e, index=i: answers.__setitem__(index, e.value))
        
        # Submit button
        ui.button('Submit', on_click=lambda: ui.navigate.to('/results')).classes("bg-blue-500 text-white px-8 py-4 text-lg mx-auto")

@ui.page('/results', dark=True)
def results_page():
    style_scores = calculate_learning_style()
    max_learning_style = max(style_scores, key=style_scores.get)
    with ui.column().classes("w-full max-w-4xl mx-auto p-8 gap-8 flex items-center justify-center h-screen"):
        ui.label(f'Your learning style is {max_learning_style}!').classes("text-3xl font-bold text-center mb-8")

        # Create and display the pie chart
        chart_image = create_pie_chart(style_scores)
        ui.image(f'data:image/png;base64,{chart_image}').classes('w-72 h-72')
        ui.button("Let's Create!", on_click=lambda: ui.navigate.to('/create_main')).classes("bg-blue-500 text-white px-8 py-4 text-lg mx-auto")

@ui.page('/', dark=True)
def main():
    with ui.column().classes("w-full max-w-4xl mx-auto p-8 gap-8 text-center"):
        ui.label("Welcome to EduCreate!").classes("text-4xl font-bold")
        ui.label("Let's start by discovering your preferred learning style by answering a few simple questions.").classes("text-xl text-gray-400")
        
        # Button to start the survey
        ui.button("Start Survey", on_click=lambda: ui.navigate.to('/survey')).classes("bg-blue-500 text-white px-8 py-4 text-lg")

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
            with ui.column().classes("w-full border rounded-lg p-4 h-64 overflow-y-auto"):
                progress_label = ui.textarea().bind_value(globals(), 'generated_progress').classes("w-full h-64").props('readonly')

        progress_dialog.open()
        
        async with websockets.connect(
            BACKEND_WS_URL,
            ping_interval=60,
            ping_timeout=600,
            ) as websocket:
            await websocket.send(file_content)
            await websocket.send(file_name)
            await websocket.send(max_learning_style)

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
                
@ui.page('/create_main', dark=True)
def create_main():
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
    with ui.dialog() as code_details_modal, ui.card().classes("w-full max-w-6xl p-4 gap-4 h-[80vh]"):
        ui.label("Generated Code Details").classes("text-xl font-bold")
        
        with ui.tabs().classes('w-full') as tabs:
            code_tab = ui.tab('Source Code')
            desc_tab = ui.tab('Description')
        
        with ui.tab_panels(tabs, value=code_tab).classes('w-full h-[70vh]'):
            with ui.tab_panel(code_tab).classes('h-full'):
                ui.code().classes("w-full h-full").bind_content(globals(), 'generated_code')
            with ui.tab_panel(desc_tab).classes('h-full'):
                ui.markdown().classes("w-full h-full overflow-y-auto").bind_content(globals(), 'generated_description')
    

ui.run(reload=False, favicon='EduCreateFav.png', title="EduCreate")