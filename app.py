from flask import Flask, render_template, request
import os
import shutil
from src.pipeline import ingest_documents, ask_question

app = Flask(__name__)
UPLOAD_FOLDER = "data/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    upload_folder = "data/uploads"

    # 🔥 DELETE old uploaded files
    if os.path.exists(upload_folder):
        shutil.rmtree(upload_folder)
    os.makedirs(upload_folder, exist_ok=True)

    files = request.files.getlist("files")

    for file in files:
        if file.filename != "":
            filepath = os.path.join(upload_folder, file.filename)
            file.save(filepath)

    message = ingest_documents()
    return render_template("index.html", message=message)


@app.route("/ask", methods=["POST"])
def ask():
    question = request.form["question"]

    # Run RAG pipeline
    result = ask_question(question)

    # Send answer + sources to UI
    return render_template(
        "index.html",
        answer=result["answer"],
        sources=result["sources"]
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
