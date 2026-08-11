# Fastapi endpoint
import uvicorn
from pathlib import Path

from  fastapi import FastAPI, Request

from database import init_db
from routes.load_conversations import loadconversationsroute
from routes.load_previous_conversations import previousconversationroute
from routes.streaming_response import streamingresponseroute
from routes.upload_documents import uploaddocumentroute



app = FastAPI()

Path("uploads").mkdir(exist_ok=True) # to save user uploaded files
Path("data").mkdir(exist_ok=True)    # to save user chat history and conversation data

init_db()
print("inside app.py file and database initialize\n")

@app.get("/home") # this is the home route
async def home(request: Request):
    # return request
    return {"message":"Working prperly"}


app.include_router(loadconversationsroute)
app.include_router(previousconversationroute)
app.include_router(streamingresponseroute)
app.include_router(uploaddocumentroute)

if __name__ == "__main__":
    uvicorn.run("app:app",host="0.0.0.0", port=8080, reload=True)