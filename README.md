# Ask My Document — Backend MVP

A PDF question-answering application using **Retrieval-Augmented Generation (RAG)** and a **local LLM**. Upload PDFs, extract and index their text with FAISS, and ask questions using retrieved document context.

The current implementation uses **FastAPI + Streamlit**. NestJS and React are planned extensions, not part of the current application.

## Current Features

- Upload one or multiple PDF documents through the Streamlit interface.
- Extract text and split it into chunks with document and page metadata.
- Store embeddings in a separate FAISS index for each document.
- Retrieve context across selected documents and rerank the combined results.
- Generate answers with a local LLM.
- Display source excerpts and links to the original PDFs.
- Expose upload, query, PDF download, and filename lookup APIs through FastAPI.

## Installation

The commands below use Bash on Linux, macOS, or WSL with Python installed as `python3`. On Windows with Git Bash and a Windows Python installation, use `python` to create the environment and `source .venv/Scripts/activate` to activate it.

```bash
git clone https://github.com/tlavu2004/ask-my-document-backend.git
cd ask-my-document-backend

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run commands from the repository root. Prepare the local model before asking questions. Embedding, reranking, and tokenizer assets may require network access on first use.

## Run the Backend

```bash
python -m uvicorn app.main:app --reload
```

Open the [API documentation](http://127.0.0.1:8000/docs).

## Run the MVP Interface

In a second Bash terminal, open the repository root, activate the same virtual environment, and start Streamlit:

```bash
source .venv/bin/activate
python -m streamlit run mvp_ui/main.py
```

The current interface expects the backend at `http://localhost:8000`.

## Local Model and Sample Documents

The current `LocalLLM` implementation uses CTransformers with this default model path:

```text
models/llama-2-7b-chat.ggmlv3.q4_1.bin
```

- [Model files referenced by the current implementation](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/tree/main)
- [Sample PDFs](https://drive.google.com/drive/folders/1_0JWnoLTJsbmswUGs5z1ULd7u4fqfzEf?usp=drive_link)

Place the compatible model file in `models/` at the repository root. To change models, update `LocalLLM` in `app/utils/llm_client.py`, including the model type and tokenizer configuration as needed. Model files are not included in this repository.

You can also generate a sample PDF locally:

```bash
python scripts/make_sample_pdf.py
```

The generated file is written to `tests/resources/sample.pdf`. The script uses Windows Arial when available; its fallback may download a font.

## Project Structure

```text
ask-my-document-backend/
├── app/
│   ├── rag/                 # Retrieval, reranking, and answer pipeline
│   ├── routes/              # Upload, query, and document endpoints
│   ├── services/            # Document processing and query orchestration
│   ├── utils/               # PDF parsing and LLM clients
│   ├── config.py
│   └── main.py
├── docs/
│   └── IMPROVEMENT_PLAN.md
├── mvp_ui/                  # Current Streamlit interface
├── scripts/                 # Environment setup and sample PDF generation
├── tests/                   # Route, service, retrieval, and LLM tests
├── data/                    # Generated uploads and indexes
├── models/                  # Local model files, supplied separately
├── fonts/                   # Generated/cached sample PDF fonts
├── .env.example
├── requirements.txt
└── README.md
```

Generated data, model files, fonts, and sample PDFs are excluded from Git. Test-mode data uses `data_test/`; configuration inconsistencies are tracked in the improvement plan.

## Known Limitations

This is an MVP with outstanding correctness, test, performance, and data-management issues. The current test suite needs alignment with the implemented API contracts. Authentication, document ownership checks, persisted conversations, and background indexing jobs are not implemented. Scanned PDFs require OCR, which is not currently supported.

The detailed review and acceptance criteria are recorded in the [Improvement and Expansion Plan](docs/IMPROVEMENT_PLAN.md).

## Roadmap

See the [Improvement and Expansion Plan](docs/IMPROVEMENT_PLAN.md) for the roadmap, target architecture, priorities, and acceptance criteria.
