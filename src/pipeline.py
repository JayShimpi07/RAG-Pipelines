import os
import shutil
from src.data_loader import load_all_documents
from src.vectorstore import FaissVectorStore
from src.search import RAGSearch


def ingest_documents():
    uploads_path = "data/uploads"
    faiss_path = "faiss_store"

    # Delete old FAISS index
    if os.path.exists(faiss_path):
        shutil.rmtree(faiss_path)

    docs = load_all_documents(uploads_path)
    if not docs:
        return "No documents found to index."

    store = FaissVectorStore(faiss_path)
    store.build_from_documents(docs)

    return "Documents indexed successfully."


def ask_question(question):
    rag = RAGSearch(persist_dir="faiss_store")
    result = rag.search_and_summarize(question)
    return result
