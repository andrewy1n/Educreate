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
        # Receive the file from the client
        file_data = await websocket.receive_bytes()
        file_name = await websocket.receive_text()

        # Save the file
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(file_data)

        # Notify the client that the file has been received
        await websocket.send_text("File received. Starting processing...")

        # Generate web app description
        await websocket.send_text("Generating web app description...")
        spec_doc = idea_agent.generate_web_app_description(file_path)
        await websocket.send_text(f"Web app description generated:\n{spec_doc}")

        # Generate code
        await websocket.send_text("Generating code...")
        generated_code = code_agent.generate_code(spec_doc)
        await websocket.send_text(f"Code generated:\n{generated_code}")

        # Send the final result as JSON
        await websocket.send_json({
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