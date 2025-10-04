import json
import uuid
from typing import Dict, Any, List
from modules.ocr import file_to_text
from .chunking import chunk_text
from .embeddings import embed_texts, get_embedding
from .vectorstore import VectorStore
from .db import SessionLocal, Document, Chunk, init_db
import os

# Optional Ollama integration
try:
    from ollama import Ollama
    _OLLAMA_AVAILABLE = True
except ImportError:
    Ollama = None
    _OLLAMA_AVAILABLE = False

class RAGPipeline:
    def __init__(self, vector_dim: int = 384, vector_persist: str = None, ollama_model: str = "llama2"):
        self.vs = VectorStore(dim=vector_dim, persist_path=vector_persist)
        self.ollama_model = ollama_model
        if _OLLAMA_AVAILABLE:
            self.ollama_client = Ollama(model=self.ollama_model)
        else:
            self.ollama_client = None
        init_db()

    def ingest_image(self, image_path: str, filename: str = None, use_gvision: bool = False) -> Dict[str, Any]:
        filename = filename or (os.path.basename(image_path) if image_path else f'doc_{uuid.uuid4()}')

        # Extract text
        text = file_to_text(image_path, use_gvision=use_gvision)

        # Chunk text
        chunks = chunk_text(text)

        # Generate embeddings
        embeddings = embed_texts(chunks, provider="sentence_transformers", model_name="all-MiniLM-L6-v2")

        # Prepare vectorstore metadata
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
        self.vs.add(embeddings, metadatas, ids)

        # Store document + chunks safely
        db = SessionLocal()
        try:
            doc = Document(filename=filename, text=text)
            db.add(doc)
            db.commit()  # assign doc.id
            # db.refresh(doc)  # ensure fully bound

            for i, c in enumerate(chunks):
                ch = Chunk(
                    document_id=doc.id,
                    content=c,
                    chunk_index=i,
                    chunk_metadata=json.dumps(metadatas[i])
                )
                db.add(ch)
            db.commit()
        finally:
            db.close()

        return {"document_id": doc.id, "num_chunks": len(chunks)}


    def query(self, query_text: str, top_k: int = 5) -> Dict[str, Any]:
        # Get embedding
        q_emb = get_embedding(query_text, provider="sentence_transformers", model_name="all-MiniLM-L6-v2")
        results = self.vs.search(q_emb, top_k=top_k)

        if not results:
            return {"answer": "No relevant chunks found.", "retrieved": []}

        retrieved_texts: List[Dict[str, Any]] = []
        db = SessionLocal()
        try:
            for result in results:
                if len(result) != 3:
                    continue  # skip malformed
                id_, dist, meta = result
                entry = {"id": id_, "distance": dist, "metadata": meta, "content": ""}
                if isinstance(meta, dict) and "chunk_index" in meta and "source" in meta:
                    doc = db.query(Document).filter(Document.filename == meta["source"]).first()
                    if doc:
                        chunk = db.query(Chunk).filter(
                            Chunk.document_id == doc.id,
                            Chunk.chunk_index == int(meta["chunk_index"])
                        ).first()
                        if chunk:
                            entry["content"] = chunk.content
                retrieved_texts.append(entry)
        finally:
            db.close()

        context = [r["content"] for r in retrieved_texts if r["content"]]
        prompt = "You are an assistant. Use the following context to answer the question."
        prompt += "\n\nContext:\n" + "\n---\n".join(context) + "\n\nQuestion: " + query_text

        answer = self._call_llm(prompt)
        return {"answer": answer, "retrieved": retrieved_texts}

    def _call_llm(self, prompt: str) -> str:
        """Call Ollama LLM if available, fallback to OpenAI if configured"""
        # Ollama
        if self.ollama_client:
            try:
                resp = self.ollama_client.chat([{"role": "user", "content": prompt}])
                return resp.get("message", "").strip()
            except Exception as e:
                return f"[LLM ERROR - Ollama]: {e}"

        # OpenAI if API key is set
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import OpenAI
                client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                    )
                resp = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role": "user", "content": prompt}]
                )

                text = resp.choices[0].message.content.strip()
                return clean_model_output(text=text)
            except Exception as e:
                return f"[LLM ERROR - OpenAI]: {e}"

        # Fallback
        return "[No LLM configured]"


import re

def clean_whitespace(text: str) -> str:
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # Strip leading/trailing spaces on each line
    text = "\n".join([line.strip() for line in text.splitlines()])
    return text

def remove_markdown(text: str) -> str:
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove bold/italic markdown
    text = re.sub(r'\*\*|\*|__|_', '', text)
    # Remove headers (#)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    return text

def flatten_tables(text: str) -> str:
    lines = text.splitlines()
    clean_lines = []
    for line in lines:
        # Skip table separator rows
        if re.match(r'^\s*\|[-\s|]+\|\s*$', line):
            continue
        # Remove table pipes and extra spaces
        line = re.sub(r'\s*\|\s*', ' | ', line)
        clean_lines.append(line.strip())
    return "\n".join(clean_lines)

def clean_model_output(text: str) -> str:
    text = clean_whitespace(text)
    text = remove_markdown(text)
    text = flatten_tables(text)
    return text
