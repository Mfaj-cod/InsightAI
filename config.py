import os

# Flask settings
class Config:
    DEBUG = True                 
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY", "nahibataunga")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_NAME = "rag_app.db"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, DB_NAME)}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    VECTOR_DIM = 384
    VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore")

# Database settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "rag_app.db"
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, DB_NAME)}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore")
VECTOR_DIM = 384    


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)


OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")  # local model
