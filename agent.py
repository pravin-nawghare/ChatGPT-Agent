# Agent Workflow
import os
import sqlite3
from pathlib import Path

from config import settings

from langgraph.graph import START, END, StateGraph, MessagesState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver

from tools import tools
from prompt import SYSTEM_PROMPT
from utils import DEFAULT_MODEL, normalize_model_name


# to store state of agent
Path("data").mkdir(exist_ok=True)

# create agent
def chat_agent(model_name: str):
    "Build agent using langgraph framework for selected LLM model"

    selected_model = normalize_model_name(model_name)

    # Initialize the llm model
    llm_model = ChatGoogleGenerativeAI(
        model=selected_model,
        temperature = 0.3, # More values gives more creative responses, drift away from grouonded responses
        streaming = True
        )

    # provide tools for the agent
    llm_with_tools = llm_model.bind_tools(tools)

    def chatbot_node(state: MessagesState):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state['messages']

        response = llm_with_tools.invoke(messages)

        return {
            "messages": [response]
        }

    tool_node = ToolNode(tools)

    graph = StateGraph(MessagesState)

    # add nodes to the graph
    graph.add_node("chatbot", chatbot_node)
    graph.add_node("tools", tool_node)

    # add edges to the graph
    graph.add_edge(START, "chatbot")
    graph.add_conditional_edges("chatbot", tools_condition)
    # if tools node is connected to END then we will receive the tool messages not the LLM response as the tool 
    # response is not given to LLM
    graph.add_edge("tools", "chatbot")

    # create connection for sqlite db
    connection = sqlite3.connect(
        "data/langgraph_checkpoints.sqlite",
        check_same_thread = False, # By default no multi-threading is allowed, but 'False' helps us to create multi-threads
    )

    custom_checkpointer = SqliteSaver(connection)

    return graph.compile(checkpointer = custom_checkpointer)

_AGENT_CACHE = {}

def get_agent(model_name: str | None = None):
    """
    Return cached Langgraph agent for selected model
    If not created yet, create it once and reuse it.
    """
    selected_model = normalize_model_name(model_name)

    if selected_model not in _AGENT_CACHE:
        _AGENT_CACHE[selected_model] = chat_agent(selected_model)

    return _AGENT_CACHE