from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os

from IdeaAgent import IdeaAgent
from CodeAgent import CodeAgent

app = FastAPI()

idea_agent = IdeaAgent()
code_agent = CodeAgent()

@app.websocket("/process-pdf")
async def process_pdf_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        file_data = await websocket.receive_bytes()
        file_name = await websocket.receive_text()

        user_preferred_style = await websocket.receive_text()

        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(file_data)

        # Notify the client that the file has been received
        await websocket.send_text("File received. Starting processing...")

        # Generate web app description
        await websocket.send_text("Generating web app description...")
        spec_doc = ""
        async for chunk in idea_agent.generate_web_app_description(file_path, user_preferred_style):
            await websocket.send_json({"type": "llm_message", "message": chunk})
            spec_doc += chunk
        print(spec_doc)
        # with open("spec_doc_example.txt", "r") as f:
        #     spec_doc = f.read()
        await websocket.send_text(f"Web app description generated...")

        # # Generate UI Components
        await websocket.send_text("Generating UI Components")
        ui_components = code_agent.generate_ui_description(spec_doc)

        # Generate code
        await websocket.send_text("Generating code...")
        generated_code = code_agent.generate_code(spec_doc, str(ui_components))
        # with open("implemented_app.py", "r", encoding="utf-8") as f:
        #     generated_code = f.read()

        # Send the final result as JSON
        await websocket.send_json({
            "type": "generated_code",
            "status": "success",
            "spec_doc": spec_doc,
            "generated_code": generated_code
        })

    except Exception as e:
        # Send error message as JSON
        await websocket.send_json({
            "status": "error",
            "error": str(e)
        })
    finally:
        await websocket.close()