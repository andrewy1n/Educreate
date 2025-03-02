import asyncio
import sys
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

class IdeaAgent:
    def __init__(self, model="deepseek-chat"):
        self.client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
        self.model = model
    
    def extract_pdf_text(self, pdf_path):
        try:
            reader = PdfReader(pdf_path)
            text = " ".join([page.extract_text() for page in reader.pages])
            return text
        except Exception as e:
            raise RuntimeError(f"PDF reading failed: {str(e)}")

    async def generate_web_app_description(self, pdf_path):
        pdf_text = self.extract_pdf_text(pdf_path)
        prompt = (
            "Analyze the content below and generate a detailed description (no code) of a simple single page frontend-focused web application that will be written using the NiceGUI framework in Python"
            "that will aid me in understanding and learning the concepts. Do not overload on features, only include aspects of the app that are absolutely necessary Include:\n"
            "- Purpose and target audience\n"
            "- Key functionalities\n"
            "- User interaction flow\n"
            "- Any special features needed\n\n"
            "Exclude any backend or user-related concepts as this application will be run from a singular file."
            f"Content:\n{pdf_text}"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
        

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please include pdf path argument")
        sys.exit(1)

    pdf_path = sys.argv[1]
    idea_agent = IdeaAgent()

    spec_doc = idea_agent.generate_web_app_description(pdf_path=pdf_path)
    print(spec_doc)
