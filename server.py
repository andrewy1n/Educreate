# backend.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
from IdeaAgent import IdeaAgent
from CodeAgent import CodeAgent

app = FastAPI()

idea_agent = IdeaAgent()
code_agent = CodeAgent()

@app.post("/process-pdf")
async def process_pdf(file: UploadFile = File(...)):
    try:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        spec_doc = idea_agent.generate_web_app_description()

        generated_code = code_agent.generate_code(spec_doc)

        return JSONResponse({
            "status": "success",
            "spec_doc": spec_doc,
            "generated_code": generated_code
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))