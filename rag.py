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
print("inside rag.py file and uploads and chroma_db folder created\n")
# Initialize the embedding model
embedding_model = HuggingFaceEmbeddings(model="sentence-transformers/all-miniLM-L6-v2")
# embedding_model = GoogleGenerativeAIEmbeddings(model = "gemini-embedding-001")
print("embedding model initialized\n")
# Initialize vector store
vector_store = Chroma(
    collection_name= "gpt-agent",
    embedding_function= embedding_model,
    persist_directory= "chroma_db"
)
print("vector store created\n")
def add_document_to_vector_store(file_path: str, thread_id: str):
    """
    Add the user uploaded files into the vector store
    """
    text = read_files_text(file_path)
    print("inside add_document_to_vector_store method\n")
    if not text.strip():
        raise ValueError("No text could be extracted from this file")

    # Initialize the text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 900,
        chunk_overlap = 150
    )
    print("splitter created\n")
    chunks = splitter.split_text(text)
    print("chunks created\n")
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
    print("Document created with chunks\n")

    # load the splitter text into vector store
    vector_store.add_documents(docs)
    print("embeddings added to vector store\n")
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
    print("inside retrieve_context method\n")
    if not docs:
        return "No revelant uploaded document content found"

    results = []
    print("retrieving context from vector store\n")
    for i,doc in enumerate(docs, start = 1):
        source = doc.metadata.get("source", "uploaded documents")
        results.append(
            f"[Source {i}: {source}]\n{doc.page_content}"
        )
    print("context reterieved\n")
    return "\n\n".join(results)