# 🚀 Resume Analyzer (RAG + Groq)

An AI-powered resume analysis system that compares a candidate's resume with a job description using **semantic search + LLM reasoning**.

---

## 🧠 What It Does

* 📄 Upload a resume (PDF / DOCX / TXT)
* 📝 Provide a job description
* ⚡ Get instant AI analysis:

  * 🎯 Match Percentage
  * 💪 Strengths
  * ⚠️ Weaknesses
  * 📈 Suggestions

---

## 🏗️ System Architecture

```
Resume → Chunking → Embeddings → FAISS → Retrieval → Groq LLM → Output
```

---

## 📦 Project Structure

| Module               | Description                                 |
| -------------------- | ------------------------------------------- |
| backend/             | FastAPI server handling API requests        |
| frontend/            | React + Vite frontend UI                    |
| core/pipeline.py     | Main pipeline (input → processing → output) |
| core/analyzer.py     | Runs RAG analysis logic                     |
| core/rag_pipeline.py | Embeddings + FAISS + LLM integration        |
| core/llm.py          | Groq LLM wrapper                            |
| core/extractor.py    | Extracts text from resume files             |
| core/utils.py        | Text preprocessing utilities                |

---

## ⚙️ Tech Stack

| Layer      | Technology                    |
| ---------- | ----------------------------- |
| Backend    | FastAPI                       |
| Frontend   | React + Vite                  |
| Embeddings | SentenceTransformers (MiniLM) |
| Vector DB  | FAISS                         |
| LLM        | Groq (LLaMA / Mixtral)        |

---

## 🔧 Backend Setup

```bash
# Navigate to project root
cd your-project

# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Run backend server
uvicorn backend.app:app --reload
```

👉 Backend runs on: [http://127.0.0.1:8000](http://127.0.0.1:8000)
👉 API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 💻 Frontend Setup

```bash
# Go to frontend folder
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

👉 Frontend runs on: [http://localhost:5173](http://localhost:5173)

---

## 🔐 Environment Variables

Create a `.env` file inside `core/`:

```
GROQ_API_KEY=your_api_key_here
LLM_MODEL=llama3-70b-8192
```

---

## 🎯 How It Works

1. Resume is uploaded and parsed
2. Text is split into chunks
3. Embeddings are generated
4. FAISS retrieves relevant chunks
5. Groq LLM analyzes resume vs job description
6. Structured feedback is returned

---

## ⚡ Features

* 📂 Supports PDF, DOCX, TXT
* ⚡ Fast inference using Groq
* 🧠 Semantic search with FAISS
* 💡 Structured AI feedback
* 🌐 Full-stack application (React + FastAPI)

---

## 🧪 Demo Flow

1. Open frontend
2. Upload resume
3. Paste job description
4. Click analyze
5. View AI-generated insights

---

## 🧠 Notes

* No GPU required (runs on CPU)
* LLM inference handled via Groq (cloud)
* Lightweight and deployable on low-resource systems

---

## 📌 Future Improvements

* JSON structured outputs (no parsing needed)
* Multi-query retrieval
* Better chunking strategy
* Deployment support

---

## 👨‍💻 Author

Swastik Nandy

---

✨ Built as a domain-agnostic RAG system for analyzing unstructured documents.
