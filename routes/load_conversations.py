# This route is responsible for loading previous conversarions on sidebar
from fastapi import APIRouter, HTTPException, Request
from database import list_conversations


loadconversationsroute = APIRouter()


@loadconversationsroute.get("/conversations")
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