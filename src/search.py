import os
from dotenv import load_dotenv
from src.vectorstore import FaissVectorStore
from src.data_loader import load_all_documents
from langchain_groq import ChatGroq

load_dotenv()


class RAGSearch:
    def __init__(
        self,
        persist_dir: str = "faiss_store",
        embedding_model: str = "all-MiniLM-L6-v2",
        llm_model: str = "llama-3.3-70b-versatile",
    ):
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)

        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")

        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            print("[INFO] Vector store not found. Building from uploaded documents...")
            docs = load_all_documents("data/uploads")
            if not docs:
                raise ValueError("No documents found in data/uploads to build vector store.")
            self.vectorstore.build_from_documents(docs)
        else:
            self.vectorstore.load()

        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables.")

        self.llm = ChatGroq(groq_api_key=groq_api_key, model_name=llm_model)
        print(f"[INFO] Groq LLM initialized: {llm_model}")

    def search_and_summarize(self, query: str, top_k: int = 5):
        print(f"[INFO] Searching for query: {query}")

        results = self.vectorstore.query(query, top_k=top_k)

        contexts = []
        sources = []

        for r in results:
            text = r.get("text", "")
            source = r.get("source", "Unknown file")
            chunk_id = r.get("chunk_id", "?")
            score = r.get("distance", 0)

            if text:
                contexts.append(text)
                snippet = text[:200].replace("\n", " ") + "..."
                sources.append(f"{source} (chunk {chunk_id}, score {score:.2f}) → {snippet}")

        if not contexts:
            return {"answer": "No relevant documents found.", "sources": []}

        context_text = "\n\n".join(contexts)

        prompt = f"""
You are a helpful assistant. Use ONLY the provided context to answer.

User Question:
{query}

Context:
{context_text}

Provide a clear answer. Do not invent information.
"""

        response = self.llm.invoke(prompt)

        return {
            "answer": response.content,
            "sources": sources
        }
