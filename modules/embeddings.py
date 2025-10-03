import os
from typing import List


try:
    from ollama import Ollama
    _OLLAMA_AVAILABLE = True
except ImportError:
    Ollama = None
    _OLLAMA_AVAILABLE = False


try:
    import openai
    _OPENAI_AVAILABLE = True
except Exception:
    openai = None
    _OPENAI_AVAILABLE = False


try:
    from sentence_transformers import SentenceTransformer
    _ST_AVAILABLE = True
except Exception:
    SentenceTransformer = None
    _ST_AVAILABLE = False


_st_model = None
_ollama_client = None

# initializing models
def _init_st_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer: # type: ignore
    global _st_model
    if _ST_AVAILABLE and _st_model is None:
        _st_model = SentenceTransformer(model_name)
    return _st_model

def _init_ollama(model_name: str = "llama2") -> Ollama: # type: ignore
    global _ollama_client
    if _OLLAMA_AVAILABLE and _ollama_client is None:
        _ollama_client = Ollama(model=model_name)
    return _ollama_client

# embedding
def get_embedding(text: str, provider: str = "sentence_transformers", model_name: str = None) -> List[float]:

    # SentenceTransformers
    if provider in ["auto", "sentence_transformers", None]:
        if _ST_AVAILABLE:
            model = _init_st_model(model_name or "all-MiniLM-L6-v2")
            return model.encode([text])[0].tolist()
    
    # OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if provider in ["auto", "openai"] and api_key and _OPENAI_AVAILABLE:
        openai.api_key = api_key
        resp = openai.Embedding.create(model="text-embedding-3-small", input=text)
        return resp['data'][0]['embedding']

    # Ollama fallback (LLM embeddings if supported)
    if provider in ["auto", "ollama"] and _OLLAMA_AVAILABLE:
        try:
            client = _init_ollama()
            resp = client.embeddings(text)
            return resp["embedding"]
        except Exception:
            pass

    raise RuntimeError(
        "No embedding provider available. "
        "Install SentenceTransformers or set OPENAI_API_KEY."
    )

def embed_texts(texts: List[str], provider: str = "sentence_transformers", model_name: str = None) -> List[List[float]]:
    """
    Embeds a list of texts.
    Returns: List of embedding vectors
    """
    return [get_embedding(t, provider=provider, model_name=model_name) for t in texts]
