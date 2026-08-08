# RAG implemation
import os
from pathlib import Path
from typing import List
from config import settings
from utils import read_files_text

from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from pypdf import PdfReader
import docx2txt

Path("uploads").mkdir(exist_ok=True)   # to store user uploaded documents
Path("chroma_db").mkdir(exist_ok=True) # to store embeddings

# Initialize the embedding model
embedding_model = HuggingFaceEmbeddings(model="sentence-transformers/all-mini-LMv6-2")
embedding_model = GoogleGenerativeAIEmbeddings(model = "gemini-embedding-001")

# Initialize vector store
vector_store = Chroma(
    collection_name= "gpt-agent",
    embedding_function= embedding_model,
    persist_directory= "chroma_db"
)

def add_document_to_vector_store(file_path: str, thread_id: str):
    """
    Add the user uploaded files into the vector store
    """
    text = read_files_text(file_path)

    if not text.strip():
        raise ValueError("No text could be extracted from this file")

    # Initialize the text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 900,
        chunk_overlap = 150
    )

    chunks = splitter.split_text(text)

    # convert the normal text into Langchain Document format
    docs: List[Document] = [
        Document(
            page_content = chunk,
            metadata = {
                "thread_id": thread_id,
                "source": Path(file_path).name
            }
        )
        for chunk in chunks
    ]

    # load the splitter text into vector store
    vector_store.add_documents(docs)

    return {
        "filename": Path(file_path).name,
        "chunks": len(docs)
    }

def retrieve_context(query: str, thread_id: str, k: int = 5) -> str:
    docs = vector_store.similarity_search(
        query,
        k=k,
        filter = {"thread_id":thread_id}
    )

    if not docs:
        return "No revelant uploaded document content found"

    results = []

    for i,doc in enumerate(docs, start = 1):
        source = doc.metadata.get("source", "uploaded documents")
        results.append(
            f"[Source {i}: {source}]\n{doc.page_content}"
        )

    return "\n\n".join(results)