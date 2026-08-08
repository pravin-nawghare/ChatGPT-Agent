# Fastapi endpoint
from agent import get_agent
from langchain.messages import HumanMessage

agent = get_agent("gemini-2.5-flash")
print("inside app.py file and get_agent method called\n")
custom_config = {
    "configurable": {
        "thread_id": "test-thread-id"
    }
}
print("config created\n")
for messagechunk, metadata in agent.stream(
    {'messages': [HumanMessage(content="Generate a short paragraph about Lakes in 100 words")]},
    config = custom_config,
    stream_mode = 'messages'
):
    if messagechunk.content:
        print(messagechunk.content, end=" ", flush=True)