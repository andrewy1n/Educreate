import asyncio
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional
from fastapi import WebSocket
from openai import OpenAI
from dotenv import load_dotenv

from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from pydantic import BaseModel
import os

load_dotenv()

class UIComponent(BaseModel):
    type: str
    description: str
    context: Optional[str] = None

class UI(BaseModel):
    component: List[UIComponent]
    
class CodeAgent:
    def __init__(self):        
        self.client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
        self.openai_client = OpenAI()
        self.vectorstore = self.init_vectorstore()

    def init_vectorstore(self):
        loader = WebBaseLoader("https://nicegui.io/documentation")
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        documents = text_splitter.split_documents(docs)

        return FAISS.from_documents(documents, OpenAIEmbeddings())
    
    def validate_module_name(self, module: str) -> bool:
        return re.match(r'^[a-zA-Z0-9_-]+$', module) is not None

    def install_module(self, module: str) -> bool:
        if not self.validate_module_name(module):
            print(f"Invalid module name: {module}")
            return False

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", module],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True)
            print(f"Successfully installed {module}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Installation failed for {module}: {e.stderr}")
            return False
        except Exception as e:
            print(f"Error installing {module}: {str(e)}")
            return False

    def get_docs_rag(self, query) -> str:
        docs = self.vectorstore.similarity_search(query, k=3)  # Retrieve top 3 relevant docs
        context = "\n\n".join([doc.page_content for doc in docs])

        return context

    async def llm_query_stream(self, prompt: str):
        print("\nSending prompt to LLM...")

        response = self.client.chat.completions.create(model="deepseek-reasoner",
                                                messages=[{"role": "user", "content": prompt}],
                                                stream=True)

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def llm_query(self, prompt: str):
        print("\nSending prompt to LLM...")

        response = self.client.chat.completions.create(model="deepseek-reasoner",
                                                messages=[{"role": "user", "content": prompt}])

        return response.choices[0].message.content

    def llm_ui_query(self, prompt: str) -> UI:
        completion = self.openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format=UI
        )

        return completion.choices[0].message.parsed

    def extract_code(self, response: str) -> str:
        print("Original Response: \n" + response) 
        code_match = re.search(r'```python(.*?)```', response, re.DOTALL)
        if not code_match:
            raise ValueError("No code block found in LLM response")
        return code_match.group(1).strip()

    def execute_code(self, code: str, attempt: int) -> dict:
        result = {"success": False, "error": "", "missing_module": None}
        timestamp = int(time.time())
         # Ensure the directory exists
        script_dir = Path("generated_scripts")
        script_dir.mkdir(parents=True, exist_ok=True)

        filename = script_dir / f"generated_code_{timestamp}_attempt_{attempt}.py"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(code)

            process = subprocess.run([sys.executable, filename],
                                    capture_output=True,
                                    text=True,
                                    timeout=30,
                                    check=True)
            result["success"] = True
        except subprocess.CalledProcessError as e:
            error_msg = f"Error {e.returncode}:\n{e.stderr}"
            result["error"] = error_msg
            # Detect missing modules
            missing_module = re.search(r"No module named '([^']+)'", e.stderr)
            if missing_module:
                result["missing_module"] = missing_module.group(1)
        except subprocess.TimeoutExpired:
            result["error"] = "Execution timed out (30 seconds)"
        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
        finally:
            if Path(filename).exists():
                Path(filename).unlink()

        return result

    def generate_ui_description(self, app_description: str) -> str:
        print("\nGenerating detailed UI components description...")

        prompt = (
            f"Based on the following app description, generate a detailed list of basic UI components(for instance, buttons, tables, forms, etc) in JSON format"
            "with their behavior and appearance:\n\n"
            "Each component should have a name and a description that describes it's behavior in the application"
            f"App description:\n{app_description}\n\n"
            "Include descriptions for each component such as what it does, how it behaves, and any specific styles or features it should have."
        )

        ui_components = self.llm_ui_query(prompt)

        for component in ui_components.component:
            print(component.type, component.description)
            component.context = self.get_docs_rag(f"{component.type}, {component.description}")

        return ui_components

    def self_heal_loop(self, initial_prompt: str, max_attempts=5, init_code="") -> str:
        error_history = []
        current_prompt = initial_prompt

        for attempt in range(1, max_attempts + 1):
            print(f"\n--- Attempt {attempt}/{max_attempts} ---")

            if attempt == 1 and init_code:
                response = init_code
            else:
                response = self.llm_query(current_prompt)
                
            try:
                code = self.extract_code(response)
                print("Extracted code:\n", code)
            except ValueError as e:
                error_msg = f"Code extraction failed: {str(e)}"
                print(error_msg)
                error_history.append(error_msg)
                current_prompt = f"{initial_prompt}\n\nPrevious error: {error_msg}"
                continue

            # Execution with installation recovery
            execution_result = self.execute_code(code, attempt)
            install_attempts = 0
            max_install_tries = 3

            while (not execution_result["success"]
                and execution_result.get("missing_module")
                and install_attempts < max_install_tries):
                module = execution_result["missing_module"]
                print(f"Missing package detected: {module}. Installing...")

                if self.install_module(module):
                    print("Re-running code after installation...")
                    execution_result = self.execute_code(code, attempt)
                    install_attempts += 1
                else:
                    error_msg = f"Failed to install {module}"
                    error_history.append(error_msg)
                    break

            if execution_result["success"]:
                return code

            print(f"{execution_result['error']} \n")

            error_history_str = "\n".join(error_history[-3:])
            
            rag_context = self.get_docs_rag(f"{execution_result['error']}")

            current_prompt = (
                f"Original task: {initial_prompt}\n\n"
                f"Previous code:\n```python\n{code}\n```\n\n"
                f"Last error:\n{execution_result['error']}\n\n"
                f"Error history:\n{error_history_str}\n\n"
                f"Context: {rag_context} \n\n"
                "Please fix this code considering the dependency issues. Make sure to regenerate the entire code")

        raise RuntimeError(f"Failed to resolve after {max_attempts} attempts")

    def generate_code(self, app_description: str, ui_description: str) -> str:
        """Main processing pipeline. Returns the generated code as a string."""
        try:
            initial_prompt = (
                "You are a code generation AI specialized in creating interactive web applications using the NiceGUI framework."
                "Your task is to utilize the given App Description and UI Description to create a functional web application"
                "The application will be executed using the command: 'python implemented_app.py'.\n"
                "Generate all required code in a single file named 'implemented_app.py' without any explanations or extra comments.\n"
                "Wrap generated code in a code block so code_match = re.search(r'```python(.*?)```', response, re.DOTALL) will find your code\n"
                "Focus on implementing core functionality with clean, maintainable code.\n\n"
                f"App description:\n{app_description}...\n\n"
                f"UI Description:\n{ui_description}"
            )

            init_code = self.llm_query(initial_prompt)

            return self.self_heal_loop(initial_prompt, init_code=init_code)

        except Exception as e:
            print(f"Critical error: {str(e)}")
            raise RuntimeError(f"Failed to generate code: {str(e)}")