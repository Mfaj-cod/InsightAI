import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename

from modules import rag_pipeline
from config import Config

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "pdf"}
app.config.from_object(Config)


os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# initializing RAG Pipeline
rag = rag_pipeline.RAGPipeline(
    vector_dim=Config.VECTOR_DIM,
    vector_persist=Config.VECTORSTORE_DIR,
    ollama_model=getattr(Config, "OLLAMA_MODEL", "llama2")
)

# helper functions
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def unique_filename(filename: str) -> str:
    """Append a UUID to prevent overwriting existing files"""
    name = secure_filename(filename)
    return f"{uuid.uuid4().hex}_{name}"

# routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for("index"))

    if file and allowed_file(file.filename):
        filename = unique_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        try:
            # Ingesting document into RAG pipeline using SentenceTransformers embeddings
            doc_info = rag.ingest_image(
                filepath,
                filename=filename,
                use_gvision=False  # True = Google Vision OCR
            )
            msg = f"Document ingested successfully. {doc_info['num_chunks']} chunks stored."
        except Exception as e:
            msg = f"Failed to ingest document: {e}"

        return render_template("docs.html", filename=filename, text_preview=msg)

    return redirect(url_for("index"))

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_query = request.form.get("query")
        if not user_query:
            return jsonify({"answer": "Please enter a query."})

        try:
            # Query RAG pipeline
            response = rag.query(user_query)
            answer = response.get("answer", "")
            retrieved = response.get("retrieved", [])
        except Exception as e:
            answer = f"Error during query: {e}"
            retrieved = []

        return jsonify({"answer": answer, "retrieved": retrieved})

    return render_template("chat.html")


if __name__ == "__main__":
    app.run(debug=True)
