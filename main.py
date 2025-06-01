from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import shutil

from fastapi.responses import JSONResponse
from src.ragflow.llm_client.zookeeper_api_client import ZooKeeperAIClient
from src.ragflow.utils.config_loader import laod_dot_env


UPLOAD_DIR = Path("temp_data")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
laod_dot_env()

app = FastAPI()

# Enable CORS (update allowed origins in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "https://kdim-ai-tool.azurewebsites.net"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/ask")
async def ask_question(
    question: str = Form(...),
    username: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    from src.ragflow.workflows.webcopy import WebCopyWorkflow
    from src.ragflow.workflows.blogs import Blog_generation
    from src.ragflow.workflows.glossary import Glossary_generation
    
    prompt_lower = question.lower()
    chat_history = []

    llm_client = ZooKeeperAIClient()

    prompt = f"""
    You are an assistant that helps identify which workflow the user wants to run.

    Available workflows: [webcopy, glossary, blog, others]

    Instructions:
    - Read the user's question carefully.
    - Identify if the user clearly mentions one of the workflows: "webcopy", "glossary", or "blog".
    - If the request clearly matches one of these, respond with **only that single word**.
    - If the user request does **not clearly match** any of the provided workflows, respond with **"others"**.

    Respond with exactly one word from the list: webcopy, glossary, blog, others.

    User question:
    "{question}"
    """

    message = [{
        "role": "user",
        "content": prompt
    }]

    prompt_lower = llm_client.generate_content_with_messages(messages=message)


    if "webcopy" in prompt_lower and file is not None:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        workflow = WebCopyWorkflow()
        encoded_doc = workflow.run(file_path, question)

        return JSONResponse(
            content={
                "answer": f'Hello {username}, your question was: "{question}"',
                "flow": "WebCopy",
                "document": {
                    "name": "web_copy.docx",
                    "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "base64": encoded_doc
                }
            }
        )

    elif "webcopy" in prompt_lower and file is None:
        workflow = WebCopyWorkflow()
        encoded_doc = workflow.run(None, question)

        return JSONResponse(
            content={
                "answer": f'Hello {username}, your question was: "{question}"',
                "flow": "WebCopy",
                "document": {
                    "name": "web_copy.docx",
                    "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "base64": encoded_doc
                }
            }
        )  
    
    elif "blog" in prompt_lower:
        workflow = Blog_generation()
        result = workflow.run(question)

        return JSONResponse(
            content = {
            "answer": result
        })
    
    elif "glossary" in prompt_lower and file is not None:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        workflow = Glossary_generation()
        result = workflow.answer(question, file_path)
        return JSONResponse(
            content = {
            "answer": result
        })
    elif "glossary" in prompt_lower and file is None:
        workflow = WebCopyWorkflow()
        result = workflow.glossary(question)
        return JSONResponse(
            content={
            "answer": result
        })

    else:
        workflow = WebCopyWorkflow()
        result = workflow.answer(question, chat_history)

        return JSONResponse(
            content={
            "answer": result
        })
