from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
import faiss
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

from document_loader import load_documents_to_vector_store
from agent import fetch_agent_with_tools, fetch_history_aware_agent_with_tools, store
from tools import get_agent_tools
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
groq_url = "https://api.groq.com/openai/v1"
groq_api_key = os.getenv("GROQ_API_KEY")

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "http://localhost:8501"},
                        r"/load_source": {"origins": "http://localhost:8501"},
                        r"/": {"origins": "http://localhost:8501"}})


# Initialize components
model_name = "llama3-70b-8192"
llm = ChatOpenAI(model=model_name, api_key=groq_api_key, base_url=groq_url)

model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)
index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))
memory = InMemoryChatMessageHistory(session_id="test-session")

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)
config = {"configurable": {"session_id": "test-session"}}


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'Flask App is Running'})


@app.route('/load_source', methods=['POST'])
def load_source():

    global vector_store

    """Handle document loading requests."""
    source_type = request.form['source_type']
    
    if source_type == "url":
        source_data = request.form['url']
    elif source_type == "file":
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        source_data = request.files['file']
        if not source_data.filename:
            return jsonify({'error': 'Empty filename'}), 400
    else:
        return jsonify({'error': 'Invalid source type'}), 400

    # Add docs to vector store
    vector_store = load_documents_to_vector_store(source_type, source_data,llm, embeddings, vector_store)

    # If Error found
    if isinstance(vector_store, BaseException):  # Check if `e` is an exception instance
        error = vector_store
        return jsonify({'error': f"Not able to load documents to vector store. \n Error: {error} "}), 500
    
    return jsonify({'message': 'Source loaded successfully'})


@app.route('/clear_chat_history', methods=['POST'])
def clear_chat_history():
    """Clear chat history for the session."""
    global store
    session_id = "test-session"  # Use the same session ID logic as in get_session_history

    if session_id in store:
        del store[session_id]  # Remove the session's history
    return jsonify({'message': 'Chat history cleared successfully'})


@app.route('/clear_rag_files', methods=['POST'])
def clear_rag_files():
    """Clears the RAG database (vector store)."""
    global vector_store, index

    # Reinitialize FAISS index and vector store to clear data
    index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))  # Reinitialize the index
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    return jsonify({'message': 'RAG database cleared successfully'})

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    global vector_store

    print(f"vector_store: {vector_store}")
    data = request.get_json()

    if not data or 'input_message' not in data:
        return jsonify({'error': 'No message provided'}), 400

    input_message = data['input_message']

    # Retriver
    print(f"vector_store type: {vector_store}")  
    retriever = vector_store.as_retriever(search_kwargs={'k': 5})
    
    # Fetch Tools
    tools = get_agent_tools(retriever)

    # Fetch Agent with given tools
    custom_agent_invoker = fetch_history_aware_agent_with_tools(llm, tools, memory)

    response = custom_agent_invoker.invoke({"input": input_message}, config)

    print(f"response: {response}")

    return jsonify({'response': response.get("output", "")})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=9997)