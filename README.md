# 🎯 SkillSync AI

### Semantic Resume–Job Matching with RAG + LLM Reasoning

**SkillSync AI** is a full-stack AI application that analyzes a candidate's resume against a job description using **semantic retrieval and LLM reasoning**.

Instead of relying only on keyword overlap, SkillSync AI converts resume content and the job description into semantic embeddings, retrieves the most relevant resume sections using **FAISS vector search**, and provides that evidence to a Groq-hosted LLM for contextual evaluation.

The result is structured feedback covering:

* 🎯 Resume–Job Match Score
* 💪 Relevant Strengths
* ⚠️ Skill & Experience Gaps
* 📈 Actionable Improvement Suggestions

> **Keywords can bluff. Embeddings have receipts. 🧠📄**

---

## ✨ Why SkillSync AI?

Traditional resume screening often depends heavily on exact keyword matching.

For example:

```text
Job Description:
"Experience developing REST APIs for machine-learning services"

Resume:
"Built FastAPI endpoints for model inference"
```

A simple keyword matcher may see only partial overlap.

SkillSync AI instead uses **dense semantic embeddings** to capture the meaning of both statements, allowing conceptually related experience to be discovered even when the wording is different.

It then applies **retrieval before generation**, so the LLM receives the resume sections most relevant to the job description rather than blindly processing the entire document.

---

# 🏗️ System Architecture

```text
                     ┌──────────────────────┐
                     │       React UI       │
                     │ Resume + Job Details │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │   FastAPI Backend    │
                     │    POST /analyze     │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │ Document Extraction  │
                     │ PDF / DOCX / TXT     │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │ Text Normalization   │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │ Resume Chunking      │
                     │ ~120 words / chunk   │
                     └──────────┬───────────┘
                                │
                                ▼
                  ┌────────────────────────────┐
                  │ SentenceTransformer MiniLM │
                  │     Dense Embeddings       │
                  └─────────────┬──────────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │     FAISS Index      │
                     │  Similarity Search   │
                     └──────────┬───────────┘
                                │
                 Job Description Embedding
                                │
                                ▼
                     ┌──────────────────────┐
                     │ Top-5 Resume Chunks  │
                     │ Semantic Retrieval   │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │      Groq LLM        │
                     │ Contextual Analysis  │
                     └──────────┬───────────┘
                                │
                                ▼
                ┌──────────────────────────────┐
                │ Match Score                  │
                │ Strengths                    │
                │ Weaknesses / Missing Skills │
                │ Recommendations              │
                └──────────────────────────────┘
```

### Pipeline in one line

```text
Resume
   → Extraction
   → Cleaning
   → Chunking
   → Embeddings
   → FAISS
   → Top-K Retrieval
   → Context Assembly
   → Groq LLM
   → Structured Feedback
```

---

# 📊 Implementation Highlights

| Metric                    | Implementation              |
| ------------------------- | --------------------------- |
| Supported resume formats  | **3**: PDF, DOCX, TXT       |
| Resume chunk size         | **120 words**               |
| Retrieval depth           | **Top 5 chunks**            |
| Maximum retrieved context | Approximately **600 words** |
| Analysis dimensions       | **4** primary outputs       |
| Embedding model           | `all-MiniLM-L6-v2`          |
| Retrieval engine          | FAISS                       |
| LLM inference             | Groq API                    |
| API endpoint              | `POST /analyze`             |
| Compute support           | CPU + optional CUDA/GPU     |

The ~600-word figure comes from retrieving up to **5 × 120-word resume chunks** before LLM analysis.

This bounds the resume evidence passed to the reasoning stage and reduces irrelevant context compared with sending the complete resume indiscriminately.

---

# 🧠 How the RAG Pipeline Works

## 1. Document Extraction

SkillSync AI accepts three common resume formats:

| Format | Parser                |
| ------ | --------------------- |
| PDF    | PyMuPDF               |
| DOCX   | python-docx           |
| TXT    | Native UTF-8 decoding |

All formats are converted into a common text representation before entering the AI pipeline.

---

## 2. Text Cleaning

Extracted document text frequently contains:

* Irregular whitespace
* Newlines
* Formatting artifacts
* Encoding inconsistencies

SkillSync AI normalizes the extracted content before chunking and embedding.

```text
Raw Document
      ↓
Text Extraction
      ↓
Whitespace Normalization
      ↓
Clean Resume Text
```

---

## 3. Resume Chunking

The resume is divided into chunks of approximately:

```text
120 words per chunk
```

Instead of embedding one large resume document, smaller chunks provide more granular semantic retrieval.

For example:

```text
Resume

├── Chunk 1 → Education
├── Chunk 2 → Python / Backend Experience
├── Chunk 3 → Machine Learning Projects
├── Chunk 4 → Cloud Experience
└── Chunk 5 → Skills
```

If the job primarily requires Python, FastAPI, and machine learning, semantic retrieval can prioritize the relevant chunks instead of unrelated sections.

---

## 4. Semantic Embeddings

SkillSync AI uses:

```text
SentenceTransformers
        +
all-MiniLM-L6-v2
```

Both resume chunks and the job description are transformed into dense numerical vector representations.

Conceptually:

```text
"Built APIs using FastAPI"
           ↓
      Embedding Model
           ↓
[0.17, -0.42, 0.81, ...]
```

The vectors represent semantic information that can be compared mathematically.

---

## 5. FAISS Vector Search

Resume embeddings are stored in a **FAISS similarity index**.

The embedded job description becomes the search query:

```text
Job Description
      ↓
JD Embedding
      ↓
FAISS Search
      ↓
Most Similar Resume Chunks
```

SkillSync AI retrieves the:

```text
Top 5
```

most relevant resume chunks.

This is the **retrieval** stage of Retrieval-Augmented Generation.

---

## 6. Context Assembly

The retrieved chunks are combined into a focused evidence context.

```text
Top Chunk 1
+
Top Chunk 2
+
Top Chunk 3
+
Top Chunk 4
+
Top Chunk 5
        ↓
Retrieved Resume Context
```

With 120-word chunks and top-5 retrieval, the LLM receives approximately **600 words of targeted resume evidence** at most from this stage.

---

## 7. LLM Reasoning

The retrieved resume evidence and job description are passed to a Groq-hosted LLM.

The model evaluates the candidate across four primary dimensions:

```text
Job Description
       +
Retrieved Resume Evidence
       ↓
     Groq LLM
       ↓
┌───────────────────────────┐
│ Match Percentage          │
│ Strengths                 │
│ Missing Skills / Gaps     │
│ Recommendations           │
└───────────────────────────┘
```

Groq handles remote LLM inference, so the application does **not require a large language model to be hosted locally**.

---

# ⚙️ Technology Stack

| Layer            | Technology           | Purpose                      |
| ---------------- | -------------------- | ---------------------------- |
| Frontend         | React                | User interface               |
| Build Tool       | Vite                 | Frontend development/build   |
| Backend          | FastAPI              | REST API                     |
| Language         | Python               | AI and backend pipeline      |
| Document Parsing | PyMuPDF              | PDF extraction               |
| Document Parsing | python-docx          | DOCX extraction              |
| Embeddings       | SentenceTransformers | Semantic representation      |
| Embedding Model  | MiniLM               | Lightweight dense embeddings |
| Vector Search    | FAISS                | Similarity retrieval         |
| ML Runtime       | PyTorch              | Embedding execution          |
| LLM Provider     | Groq                 | Hosted LLM inference         |
| API Data         | multipart/form-data  | Resume + JD upload           |
| Environment      | python-dotenv        | Configuration                |
| Version Control  | Git / GitHub         | Source management            |

---

# 📦 Project Structure

```text
Resume-Analyser/
│
├── backend/
│   ├── app.py
│   └── main.py
│
├── core/
│   ├── analyzer.py
│   ├── embedder.py
│   ├── extractor.py
│   ├── feedback.py
│   ├── llm.py
│   ├── pipeline.py
│   ├── rag_pipeline.py
│   └── utils.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── components/
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── samples/
├── test.py
├── requirements.txt
└── readme.md
```

### Main Components

| Module                 | Responsibility                               |
| ---------------------- | -------------------------------------------- |
| `backend/app.py`       | FastAPI application and `/analyze` endpoint  |
| `core/pipeline.py`     | End-to-end resume processing orchestration   |
| `core/analyzer.py`     | Embedding, FAISS retrieval, and LLM analysis |
| `core/extractor.py`    | PDF, DOCX, and TXT extraction                |
| `core/llm.py`          | Groq client and LLM inference                |
| `core/utils.py`        | Text normalization utilities                 |
| `frontend/src/App.jsx` | Main React application interface             |
| `test.py`              | Local end-to-end pipeline test               |

---

# 🚀 Getting Started

## Prerequisites

You will need:

```text
Python
Node.js + npm
Git
Groq API Key
```

A GPU is **not required**.

CUDA-compatible hardware can optionally be used for local embedding computation when available.

---

# 1️⃣ Clone the Repository

```bash
git clone https://github.com/swastik-nandy/Resume-Analyser.git
cd Resume-Analyser
```

---

# 2️⃣ Create a Python Virtual Environment

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```cmd
python -m venv venv
venv\Scripts\activate
```

---

# 3️⃣ Install Backend Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

The project currently includes dependencies for:

* FastAPI
* Uvicorn
* SentenceTransformers
* PyTorch
* FAISS
* Groq
* PyMuPDF
* python-docx
* LangChain utilities
* Hugging Face tooling

---

## ⚠️ FAISS CPU/GPU Note

The current `requirements.txt` includes both CPU and GPU-related FAISS packages.

If you are running on a machine without CUDA and encounter an installation problem related to `faiss-gpu`, use the CPU implementation:

```bash
pip uninstall -y faiss-gpu
pip install faiss-cpu
```

The application already contains fallback logic so FAISS can operate without GPU acceleration.

---

# 4️⃣ Configure Groq

Create:

```text
core/.env
```

Add:

```env
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=your_groq_model_name
```

For example:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxx
LLM_MODEL=your-enabled-model
```

> Do not commit your `.env` file or API key to GitHub.

`LLM_MODEL` is configurable because available Groq model identifiers can change over time.

---

# 5️⃣ Start the Backend

From the project root:

```bash
uvicorn backend.app:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI automatically exposes interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

---

# 6️⃣ Check Backend Health

Open:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "resume-analyzer"
}
```

---

# 7️⃣ Install the Frontend

Open another terminal:

```bash
cd frontend
npm install
```

---

# 8️⃣ Start the React Application

```bash
npm run dev
```

Vite will normally expose the frontend at:

```text
http://localhost:5173
```

Keep both terminals running:

```text
Terminal 1
FastAPI
localhost:8000

Terminal 2
React + Vite
localhost:5173
```

---

# 🖥️ Using SkillSync AI

Once both services are running:

1. Open the React application.
2. Upload a PDF, DOCX, or TXT resume.
3. Paste the target job description.
4. Click the analysis button.
5. Wait for the RAG pipeline to process the resume.
6. Review the generated match analysis.

The result contains:

```text
🎯 Match Score
💪 Strengths
⚠️ Weaknesses / Missing Skills
📈 Recommendations
```

---

# 🔌 API Usage

The primary backend endpoint is:

```http
POST /analyze
```

It expects:

| Field     | Type   | Description              |
| --------- | ------ | ------------------------ |
| `file`    | File   | PDF, DOCX, or TXT resume |
| `jd_text` | String | Target job description   |

Example using `curl`:

```bash
curl -X POST \
  http://127.0.0.1:8000/analyze \
  -F "file=@samples/resume.pdf" \
  -F "jd_text=Looking for a Python AI Engineer with FastAPI and RAG experience."
```

Example response structure:

```json
{
  "match_percentage": "82",
  "strengths": "...",
  "weaknesses": "...",
  "suggestions": "...",
  "raw_output": "..."
}
```

---

# 🧪 Running the Local Pipeline Test

A basic end-to-end test script is included.

Place a sample resume at:

```text
samples/resume.pdf
```

Then run:

```bash
python test.py
```

The test exercises:

```text
Resume
   ↓
Extraction
   ↓
Chunking
   ↓
Embedding
   ↓
FAISS Retrieval
   ↓
Groq
   ↓
Analysis
```

and displays the resulting match analysis in the terminal.

---

# 💡 What Makes This Project Interesting?

SkillSync AI is more than a prompt wrapped in a frontend.

The application separates the document intelligence workflow into distinct stages:

```text
Document Processing
        ↓
Semantic Representation
        ↓
Information Retrieval
        ↓
Context Construction
        ↓
LLM Reasoning
        ↓
Application Output
```

This separation allows individual stages to be replaced or improved independently.

For example:

```text
MiniLM
   ↓
BGE / E5 / another embedding model
```

or:

```text
FAISS
   ↓
Qdrant / Milvus / pgvector
```

without redesigning the entire application.

---

# 🆚 RAG vs Direct LLM Processing

A simpler implementation could send the complete resume directly to an LLM.

SkillSync AI instead performs retrieval first.

### Direct LLM approach

```text
Entire Resume + JD
        ↓
       LLM
```

### SkillSync AI

```text
Resume
   ↓
Chunk
   ↓
Embed
   ↓
Retrieve Relevant Evidence
   ↓
Relevant Evidence + JD
   ↓
LLM
```

The second architecture creates an explicit retrieval layer and makes it possible to control which evidence enters the model context.

---

# ⚡ Hardware Portability

The embedding pipeline detects whether CUDA is available.

```text
CUDA Available?
     │
 ┌───┴────┐
 │        │
Yes       No
 │        │
GPU      CPU
 │        │
 └───┬────┘
     ↓
Embedding Pipeline
```

FAISS indexing similarly attempts GPU execution and falls back to CPU when GPU FAISS is unavailable.

This makes the project usable on both:

* GPU development machines
* CPU-only laptops and servers

The LLM itself is hosted through Groq, so large-model inference does not consume local GPU memory.

---

# 🔐 Security Notes

The Groq API key is loaded through environment configuration rather than hardcoded application logic.

Never commit:

```text
core/.env
```

or any file containing:

```text
GROQ_API_KEY
```

to version control.

For production deployment, secrets should be supplied using the target platform's secret-management system instead of storing them in the repository.

---

# 🛠️ Current Limitations

SkillSync AI is currently a portfolio/prototype implementation rather than a production ATS platform.

Current limitations include:

* FAISS index is constructed per analysis
* No persistent vector database
* No authentication or user accounts
* No persistent analysis history
* No retrieval evaluation benchmark yet
* LLM output parsing can still depend on generated formatting
* No production deployment configuration
* No OCR pipeline for scanned-image resumes

Making these boundaries explicit is intentional. Future improvements should be measured rather than hidden behind inflated benchmark claims.

---

# 🗺️ Roadmap

Potential future improvements:

* [ ] Structured LLM outputs using strict schemas
* [ ] Retrieval evaluation dataset
* [ ] Precision@K / Recall@K benchmarking
* [ ] Semantic or structure-aware chunking
* [ ] Hybrid dense + lexical retrieval
* [ ] Cross-encoder reranking
* [ ] Persistent vector storage
* [ ] Resume section detection
* [ ] Multi-query retrieval
* [ ] OCR support for scanned PDFs
* [ ] Authentication and analysis history
* [ ] Containerized deployment
* [ ] Automated backend/frontend testing
* [ ] CI/CD pipeline
* [ ] Cloud deployment

---

# 📈 Future Evaluation

Instead of claiming unverified improvements, future versions can benchmark SkillSync AI using measurable retrieval and system metrics:

| Metric                 | Purpose                                                 |
| ---------------------- | ------------------------------------------------------- |
| Precision@K            | Measures retrieved chunk relevance                      |
| Recall@K               | Measures whether important resume evidence is retrieved |
| MRR                    | Evaluates ranking quality                               |
| Retrieval latency      | Measures FAISS search performance                       |
| End-to-end latency     | Measures complete analysis time                         |
| Context tokens         | Measures LLM context efficiency                         |
| LLM output consistency | Evaluates structured response reliability               |

This would allow future improvements to embedding models, chunking strategies, and retrieval methods to be compared objectively.

---

# 🤝 Contributing

Contributions, experiments, and suggestions are welcome.

A typical workflow:

```bash
git checkout -b feature/my-improvement
git add .
git commit -m "feat: describe improvement"
git push origin feature/my-improvement
```

Then open a pull request.

Potential contribution areas include:

* Retrieval quality
* Resume parsing
* UI/UX
* Evaluation
* Embedding models
* Prompt engineering
* Testing
* Deployment

---

# 📜 License

This repository does not currently contain a project-level license file.

If SkillSync AI is intended to be open source, an **MIT License** is a suitable option for a portfolio project because it permits use, modification, and redistribution while retaining the copyright and license notice.

After adding a `LICENSE` file, this section can be changed to:

```text
This project is licensed under the MIT License.
See LICENSE for details.
```

---

# 👨‍💻 Author

**Swastik Nandy**

Engineering student exploring:

* Artificial Intelligence
* Retrieval-Augmented Generation
* LLM Systems
* Information Retrieval
* Backend Engineering
* Applied Machine Learning

---

# ⭐ SkillSync AI

```text
Resume.pdf
    +
Job Description
    ↓
Semantic Retrieval
    ↓
Relevant Evidence
    ↓
LLM Reasoning
    ↓
"Here's where you match.
 Here's where you don't.
 Here's what you can improve."
```

**Keywords can bluff. Embeddings have receipts. 🧠📄**

If SkillSync AI helped you explore RAG, semantic search, or resume intelligence, consider giving the repository a ⭐.
