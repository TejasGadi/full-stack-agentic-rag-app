# Agentic RAG (Retrieval-Augmented Generation)

A powerful AI chat assistant that combines agent-based interactions with RAG capabilities, allowing users to query their documents intelligently. Built with Flask, Streamlit, and LangChain.

## 🌟 Features

- **Multiple-Document Support**: Upload multiple PDF files simultaneously
- **URL Processing**: Add web pages as knowledge sources
- **Intelligent Querying**: Uses multiple tools including:
  - RAG-based document search
  - Wikipedia lookups
  - Web search capabilities
  - Arxiv paper search
- **Interactive Chat Interface**: Clean and intuitive UI built with Streamlit
- **Real-time Processing**: Immediate feedback on document processing status
- **Session Management**: Maintains chat history and document context

## 🛠️ Technology Stack

- **Backend**: Flask
- **Frontend**: Streamlit
- **AI/ML Components**:
  - LangChain
  - Groq
  - FAISS Vector Store
  - Ollama Embeddings
- **Additional Tools**:
  - Flask-CORS for cross-origin support
  - Various LangChain tools (Wikipedia, DuckDuckGo, Arxiv)

## 📋 Prerequisites

- Python 3.8+
- Groq API key
- Docker & Docker Compose installed

## 🚀 Installation

### Using Virtual Environment

1. Clone the repository:
```bash
git https://github.com/TejasGadi/full-stack-agentic-rag-app.git
cd full-stack-agentic-rag-app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

4. Create environment variable files:

**backend/.env**
```env
GROQ_API_KEY=<your-groq-api-key>
```

**frontend/.env**
```env
FLASK_BASE_URL=http://backend:9997
```

### Running with Virtual Environment

1. Start the Flask backend:
```bash
cd backend
python app.py
```
The backend will run on `http://localhost:9997`

2. In a new terminal, start the Streamlit frontend:
```bash
cd frontend
streamlit run streamlit.py
```
The frontend will be available at `http://localhost:8501`

### Using Docker Compose

1. Ensure Docker and Docker Compose are installed.
2. Set up environment variables in `frontend/.env` and `backend/.env` as described above.
3. Build and start the project using Docker Compose:
```bash
docker-compose up --build
```
4. The backend will be available at `http://localhost:9997`, and the frontend at `http://localhost:8501`.

## 📂 Project Structure

```
agentic-rag/
├── backend/
│   ├── __pycache__/
│   ├── temp_files/
│   ├── .env
│   ├── agent.py
│   ├── app.py
│   ├── document_loader.py
│   ├── tools.py
│   ├── requirements.txt
│   ├── Dockerfile
├── frontend/
│   ├── .env
│   ├── streamlit.py
│   ├── requirements.txt
│   ├── Dockerfile
├── venv/
├── docker-compose.yml
```

## 🛠️ Configuration

The application can be configured through several environment variables:

- `GROQ_API_KEY`: Your Groq API key
- `FLASK_BASE_URL`: Backend URL (default: http://localhost:9997)
