from langchain_community.document_loaders import WebBaseLoader, TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_ollama import OllamaEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import bs4
import os
from uuid import uuid4

# Document loading helper
def load_documents_to_vector_store(source_type: str, source_data, llm, embeddings, vector_store):
    """Load and index documents from URL or file."""
    try:
        if source_type == "url":
            loader = WebBaseLoader(
                web_path=source_data
            )
            documents = loader.load()
        elif source_type == "file":
            os.makedirs("temp_files", exist_ok=True)
            file_path = f"temp_files/{source_data.filename}"
            source_data.save(file_path)
            
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            else:
                loader = TextLoader(file_path)
            documents = loader.load()
            os.remove(file_path)
        else:
            return "Invalid source type"

        splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=300)
        chunks = splitter.split_documents(documents)
        print(f"documents: {documents}")
        ids = [str(uuid4()) for _ in range(len(chunks))]
        vector_store.add_documents(documents = chunks, ids=ids)
        return vector_store
        
    except Exception as e:
        return e