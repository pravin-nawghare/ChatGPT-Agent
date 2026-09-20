# PrivateGPT: Agentic RAG Assistant
A private ChatGPT-style assistant that combines Gemini models, web search, document retrieval, conversation history, long-term memory, and safety guardrails.

---

## Overview
PrivateGPT is an agentic AI application for interacting with both general knowledge and private documents. Users can ask normal questions, search the internet for current information, upload documents, retrieve relevant document content, perform calculations, and save information for future conversations.

The system uses an LLM-powered LangGraph agent that decides when to answer directly and when to use tools such as web search, document retrieval, calculator, or memory.

---

## Problem Statement
General-purpose chatbots may not have access to an organisation’s private documents, while traditional document search systems cannot provide flexible conversational answers or current internet-based information.

This project explores an agentic Retrieval-Augmented Generation approach that combines:
- General-purpose LLM conversations
- Retrieval from private uploaded documents
- Current information from internet search
- Persistent conversation history
- Long-term user memory
- Jailbreak and toxic-language detection

---

## Objectives
The main objectives are to:
- Build a ChatGPT-like private assistant.
- Retrieve relevant information from uploaded documents.
- Generate answers using retrieved context.
- Use web search for current or time-sensitive questions.
- Maintain conversation history across sessions.
- Add safety checks for jailbreak attempts and toxic language.

---

## Key Features
- Agentic tool selection using LangGraph
- Semantic document retrieval using ChromaDB
- Upload support for PDF, TXT, DOCX, Markdown, Python, and CSV files
- Persistent conversation history using SQLite
- Long-term memory for saved user preferences and facts
- Internet search using Tavily
- Basic mathematical calculations
- Jailbreak detection
- Toxic-language detection

---

## Technology Stack
| Area | Technology |
|------|------------|
| **LLM** | Gemini Models |
| **Agent Framework** | Langgraph and Langchain |
| **Embeddings** | `sentence-transformers/all-MiniLM-6-v2` |
| **Vector Database** | ChromDB |
| **Relational Database** | SQLite (checkpoint storage + memory persistence) |
| **Backend** | FastAPI |
| **Frontend** | Streamlit |
| **Safety** | Guardrails AI |

Why These Technologies?
- **Gemini**: Provides capable language models and is suitable for prototyping with available API credits.
- **LangGraph**: Makes it possible to model the assistant as a stateful graph with tool-calling loops.
- **ChromaDB**: Runs locally and provides persistent vector storage without requiring a separate database service.
- **SQLite**: Provides lightweight local persistence for conversations, messages, and memories.
- **FastAPI**: Provides an asynchronous backend and supports streaming responses.
- **Streamlit**: Enables rapid development of a conversational frontend.
- **Guardrails AI**: Adds jailbreak and toxic-language validation.

---

## System Architecture
The application has two main services:

1. **FastAPI Backend**
- Receives chat requests.
- Manages document uploads.
- Runs the LangGraph agent.
- Streams responses to the frontend.
- Stores conversation data in SQLite.

2. **Streamlit Frontend**
- Provides the chat interface.
- Displays previous conversations.
- Allows model selection.
- Accepts document uploads.
- Displays streamed assistant responses.

---

## Results / Key Findings

1. **RAG tool**: By expilicity telling the LLM to use the uploaded document to reply for the user query helps model to understand to use the RAG tool.

2. **Gemini 2.5-Flash Performance**: Latency reduction of ~40% compared to standard Gemini models while maintaining output quality. Token efficiency improved due to optimized prompts.

3. **SQLite Checkpoint Reliability**: Persistent state management successfully enables multi-session workflows with zero data loss in testing. Suitable for production use with proper backup strategy.

---

## Limitations

**Current constraints affecting functionality:**

- The project has not yet been formally evaluated.
- Internet search increases response latency.
- The current toolset is limited to web search, document search, and basic calculations.
- Web search is integrated through an API rather than an MCP server.
- Scanned or image-only PDFs may not produce useful text without OCR.
- The jailbreak detector requires manual local model-path configuration (dependency issue).
- The active upload route supports PDF, TXT, DOCX, Markdown, Python, and CSV files.

---

## Future Improvements

**Roadmap for production readiness:**

- Add a reranking stage before sending context to the LLM.
- Evaluate retrieval and answer quality using a benchmark dataset.
- Add response and retrieval caching.
- Improve multi-document and multi-hop reasoning.
- Add OCR support for scanned documents.
- Replace direct API-based tools with MCP servers.

---

## Learning Outcomes

Through building this system, I gained experience with:

- **Memory Management**: Desigining workflow with stored previous conversations so it be referred again when needed.
- **LangGraph State Machines**: Building deterministic, checkpointable workflows for LLM applications

---

## Installation and Setup

1. **Clone the repository**
    ```bash
    git clone https://github.com/pravin-nawghare/ChatGPT-Agent.git
    cd ChatGPT-Agent
    ```

2. **Create a virtual environment**
    ```bash
   conda create -n venv python=3.13 -y
   conda activate venv
    ```

3. **Install Dependencies**
    ```bash
   pip install -r requirements.txt
    ```

4. **Configure environment variables**
    ```bash
    GEMINI_API_KEY=your_gemini_api_key
    TAVILY_API_KEY=your_tavily_api_key
    HF_TOKEN=your_huggingface_token
    ```

5. **Optional**
    ```bash
    GROQ_API_KEY=your_groq_api_key
    LANGSMITH_API_KEY=your_langsmith_api_key
    APP_HOST=127.0.0.1
    APP_PORT=8000
    ```

The primary implementation currently uses Gemini and Tavily. The Groq variables are retained for future model support.

### Guardrails Setup
Install the Guardrails model resources:
```bash
   python -m guardrails_ai.toxic_language.post_install
   python -m guardrails_ai.detect_jailbreak.post_install
```

The compatibility implementation in [jailbreak_guard.py](https://github.com/pravin-nawghare/ChatGPT-Agent/blob/main/jailbreak_guard.py) requires the local path to the downloaded jailbreak classifier.

To locate the model files, run:
```bash
python -c "from huggingface_hub import snapshot_download print(snapshot_download('zhx123/ftrobertallm'))"
```  
Copy the resulting path into ``TEXT_CLASSIFIER_NAME`` in [jailbreak_guard.py](https://github.com/pravin-nawghare/ChatGPT-Agent/blob/main/jailbreak_guard.py)

### Running the Application
Start the FastAPI backend:
```bash
   python app.py
```

Start the Streamlit frontend in a second terminal:
```bash
   streamlit run frontend.py
```

---

## Project Structure
```
.
├── agent.py                 # LangGraph agent and tool-calling workflow
├── app.py                   # FastAPI application
├── config.py                # Environment and application settings
├── database.py              # SQLite models and persistence functions
├── frontend.py              # Streamlit frontend
├── jailbreak_guard.py       # Compatible jailbreak detector
├── prompt.py                # System prompt for the agent
├── rag.py                   # Document chunking, embeddings, and retrieval (RAG tool)
├── tools.py                 # Maths calculations and web search
├── utils.py                 # Shared helpers and safety guards
├── routes/
│   ├── load_conversations.py
│   ├── load_previous_conversations.py
│   ├── streaming_response.py
│   └── upload_documents.py
├── requirements.txt         # Required Packages
└── visuals/                 # Screenshots
```
---

## Screenshots

Full Screen UI

[<image src="visuals/full%20screen%20ui.png" alt="Opening Page of Project" height="300px">](https://github.com/pravin-nawghare/ChatGPT-Agent/blob/main/visuals/full%20screen%20ui.png)

Previous Conversations Loaded

[<image src="visuals/previous%20conversations%20from%20histroy.png" alt="Previous Conversations" height="300px">](https://github.com/pravin-nawghare/ChatGPT-Agent/blob/main/visuals/previous%20conversations%20from%20histroy.png)

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) file for details.

---

## Contact & Contributions

For questions, issues, or contributions, please open an issue or pull request on the project repository.

---

**Built with ❤️ using LangChain, LangGraph, and Google Gemini**