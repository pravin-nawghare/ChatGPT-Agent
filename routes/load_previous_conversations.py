# This route is responsible for loading the previous conversation user had
from fastapi import APIRouter, HTTPException, Request
from database import get_user_chat_history


previousconversationroute = APIRouter()


@previousconversationroute.get("/history/{thread_id}")
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