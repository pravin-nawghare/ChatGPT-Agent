# This route is responsible getiing streaming responses on LLM
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from langchain_core.messages import HumanMessage
from agent import get_agent
from utils import sse_data, should_stream_chunk, extract_text_from_chunk
from database import create_or_update_conservation, save_user_chat_message
from tools import set_current_thread


streamingresponseroute = APIRouter()

@streamingresponseroute.post("/chat/stream")
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