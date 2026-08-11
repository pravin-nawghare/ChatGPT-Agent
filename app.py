# Fastapi endpoint
import os
import json
import uuid
import uvicorn
from pathlib import Path

from  fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse

from agent import get_agent
from config import settings
from database import (init_db, save_user_chat_message, get_user_chat_history, 
                      create_or_update_conservation, list_conversations)
from rag import add_document_to_vector_store
from tools import set_current_thread
from utils import sse_data, should_stream_chunk, extract_text_from_chunk

from langchain_core.messages import HumanMessage

setting = settings
# agent = get_agent("gemini-2.5-flash")
# print("get_agent method called\n")
# custom_config = {
#     "configurable": {
#         "thread_id": "test-thread-id"
#     }
# }
# print("config created\n")
# for messagechunk, metadata in agent.stream(
#     {'messages': [HumanMessage(content="Generate a short paragraph about Lakes in 100 words")]},
#     config = custom_config,
#     stream_mode = 'messages'
# ):
#     if messagechunk.content:
#         print(messagechunk.content, end=" ", flush=True)

app = FastAPI()

Path("uploads").mkdir(exist_ok=True) # to save user uploaded files
Path("data").mkdir(exist_ok=True)    # to save user chat history and conversation data

init_db()
print("inside app.py file and database initialize\n")

@app.get("/home") # this is the home route
async def home(request: Request):
    # return request
    return {"message":"Working prperly"}

@app.get("/conversations")
async def conversations(): # view previous conversation on sidebar
    items = list_conversations()

    return {
        "conversations": [
            {
                "thread_id": item.thread_id,
                "title" : item.title,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat()
            }
            for item in items
        ]
    }

@app.get("/history/{thread_id}")
async def history(thread_id: str): # load previous conversation on chat page
    messages = get_user_chat_history(thread_id=thread_id)

    return {
        "messages": [
            {
                "role":msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
    }

@app.post("/upload")  # route to upload user files and get processed and added to vector store for rag 
async def upload_document(
    file: UploadFile = File(...),
    thread_id: str = Form(...)
    ):
    try:
        allowed_extensions = ['.pdf', '.txt', '.docx', '.md', '.py', '.csv']

        filename = file.filename or "uploaded_file"
        suffix = Path(filename).suffix.lower()

        if suffix not in allowed_extensions:
            return JSONResponse(
                {
                    "success": False,
                    "message": "Unsupported file format. Upload only .pdf, .txt, .docx', .md, .py, .csv files"
                },
                status_code=400
            )

        file_id = str(uuid.uuid4())
        safe_filename = filename.replace(" ","_")
        file_path = f"Uploads/{file_id}_{safe_filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        create_or_update_conservation(first_message="Uploaded documents",thread_id=thread_id)

        result = add_document_to_vector_store(
            file_path=file_path,
            thread_id=thread_id
        )

        return JSONResponse({
            "success": True,
            "message": f"Uploaded {result['filename']} and created {result['chunks']} chunks."
        })

    except Exception as e:
        return JSONResponse(
            {
                "success": False,
                "message": str(e)
            },
            status_code=500
        )

@app.post("/chat/stream")  # to get chat stream at frontend
async def chat_stream(request: Request):
    try:
        data = await request.json()
    except Exception as e:
        return JSONResponse({
            "error": "invalid JSON body"
        }, status_code= 400
    )

    user_message = data.get("message", "")
    thread_id = data.get("thread_id", "default")
    selected_model = data.get("model", "gemini-2.5-flash")

    if not user_message.strip():
        return JSONResponse({
                "error": "Message is required"
        }, 
            status_code= 400
    )

    agent = get_agent(selected_model)

    create_or_update_conservation(thread_id=thread_id, first_message=user_message) # add the conversation to database if not already present or update if already present
    save_user_chat_message(thread_id, "user", user_message) # save current chat into database

    set_current_thread(thread_id)

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    def event_generator(): # this function will stream the response from the agent to the frontend using fastapi StreamingResponse
        final_answer = ""

        try:
            inputs = {
                "messages": [
                    HumanMessage(content=user_message)
                ]
            }

            for chunk, metadata in agent.stream(
                inputs,
                config=config,
                stream_mode = "messages"
            ):
                if not should_stream_chunk(chunk, metadata):
                    continue

                token = extract_text_from_chunk(chunk)

                if token:
                    final_answer += token
                    yield sse_data({"token":token})

            if final_answer.strip():
                save_user_chat_message(thread_id, "assistant", final_answer)

            yield sse_data({"done": True})

        except Exception as e:
            yield sse_data({"error": str(e)})
            yield sse_data({"done": True})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


if __name__ == "__main__":
    uvicorn.run("app:app",host="0.0.0.0", port=8080, reload=True)