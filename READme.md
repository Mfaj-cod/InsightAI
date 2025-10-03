> InsightAI :– Retrieval-Augmented Generation (RAG) App

    InsightAI is a Retrieval-Augmented Generation (RAG) web application built with Flask (backend) and HTML + Bootstrap (frontend).
        It enables you to upload documents/images, extract text using OCR, create embeddings, store them in a vector database, and query the knowledge base with the help of LLMs like Ollama’s open-source models.

> Features:-

    🖼 Upload documents/images (PNG, JPG, JPEG, PDF)

    🔎 OCR text extraction (Tesseract and Google Vision API)

    ✂ Text chunking for better retrieval

    🧠 Embeddings generation (via HuggingFace/Sentence-Transformers or OpenAI/Ollama)

    📦 Vector database support (FAISS)

    💾 SQLAlchemy integration for document metadata storage

    💬 Chat with your documents using RAG pipeline and LLM (Ollama by default and OpenAI on fallback)

    🌐 Frontend built with Flask templates (Bootstrap, JS, CSS)


> Project Structure:-

InsightAI/
│── app.py                # Flask app entry point
│── config.py             # Configuration settings
│── requirements.txt      # Dependencies
│── README.md             # Project documentation
│
├── modules/              
│   ├── __init__.py
│   ├── ocr.py            # OCR functions
│   ├── chunking.py       # Text chunking
│   ├── embeddings.py     # Embedding generation
│   ├── vectorstore.py    # Vector DB operations
│   ├── rag_pipeline.py   # RAG pipeline logic
│   └── db.py             # SQLalchemy DB models
│
├── templates/           
│   ├── base.html
│   ├── index.html
│   ├── docs.html
│   └── chat.html
│
├── static/               
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── uploads/          # Uploaded files
│
└── tests/                
    ├── test_ocr.py
    ├── test_embeddings.py
    ├── test_vectorstore.py
    └── test_rag_pipeline.py


> Installation:-

    1. Clone the repository
    git clone https://github.com/yourusername/InsightAI.git
    cd InsightAI

    2. Create a virtual environment
    python -m venv venv
    source venv/bin/activate      # Linux/Mac
    venv\Scripts\activate         # Windows

    3. Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt

    4. (Optional) Install FAISS for vector search
    pip install faiss-cpu

    5. Install and run Ollama (if using local models)

    Download Ollama

    Verify installation:

    ollama run llama2

    ▶️ Running the App
    python app.py


    The app will be available at http://127.0.0.1:5000/

> Usage:-

    Open the web app in your browser.

    Upload a PDF/image document.

    The system will extract text, chunk it, and store embeddings.

    Go to Chat and ask questions related to your uploaded documents.


> Future Improvements:-

    Add support for multi-document queries

    Integrate LangChain for pipeline flexibility

    UI enhancements (dark mode, history view)

    Dockerize the app for deployment

    Add cloud vector DBs (Pinecone, Weaviate, Qdrant)

> License:-

    This project is licensed under the MIT License – feel free to use and modify it.


> System design:-


                ┌─────────────────────────┐
                │       User (Web)        │
                │  • Upload document/img  │
                │  • Ask questions (chat) │
                └───────────┬─────────────┘
                            │
                            ▼
                ┌─────────────────────────┐
                │     Flask Web Server    │
                │(Routes + Business Logic)│
                └───────────┬─────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────────┐
│   OCR Engine   │  │ Vector Database│  │    LLM API         │
│ (Tesseract /   │  │ (Qdrant / Pine-│  │ (OpenAI GPT /      │
│ Google Vision) │  │cone / Weaviate)│  │ LLaMA local model) │
└────────────────┘  └────────────────┘  └────────────────────┘
        │                   ▲                   ▲
        ▼                   │                   │
  Extracted Text ───────────┼── Embeddings ─────┘
                            │
                            ▼
                ┌─────────────────────────┐
                │   Document Store (DB)   │
                │ Metadata + Original Docs│
                └─────────────────────────┘


🔹 Flow Explanation

Upload Document (Web Frontend)

    User uploads PDF/image via Bootstrap form.

    Flask handles the file and sends it to OCR.

OCR & Preprocessing

    OCR extracts raw text.

    Flask cleans and chunks text.

Embedding + Storage

    Each chunk is embedded (OpenAI embeddings or SentenceTransformers).

    Stored in a vector DB (FAISS locally).

    Also save metadata in a relational DB (SQLAlchemy) for tracking.

Query Phase

    User types a question.

    Flask generates embedding of the query.

    Vector DB retrieves top-k similar chunks.

LLM Answering

    Retrieved chunks + user question sent to LLM (OpenAI API or local).

    LLM generates context-aware answer.

    Response Display

    Flask returns the answer to frontend.

    Bootstrap renders it in a chat-style UI.



