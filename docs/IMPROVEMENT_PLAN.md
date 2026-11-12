# Ask My Document Improvement and Expansion Plan

## 1. Scope and Decisions

This document describes the proposed backlog and architecture, not features already implemented. The current stack is FastAPI + Streamlit + FAISS + a local LLM. Existing flows support uploading multiple PDFs, building indexes, retrieval, reranking, answer generation, and source display.

The next goal is a reliable local demo with React as the frontend, NestJS for application logic, and FastAPI for AI processing. Hosting, a domain, paid cloud services, and Kubernetes are not required. Introduce components only when their implementation phase requires them.

Key decisions:

- Fix the Python foundation before separating services.
- Keep PDF parsing, chunking, embedding, retrieval, reranking, and LLM integration in Python.
- Use NestJS for users, access control, documents, conversations, and job orchestration.
- Replace Streamlit with React + TypeScript + Vite as the main UI.
- A localhost demo is sufficient; public deployment is optional.
- Keep FAISS initially; a separate vector database is not required yet.
- Migrating to Spring Boot is outside this plan.

The review covered all Git-managed files through static inspection. Syntax checks passed for 23 Python files. The test suite could not run because pytest was missing from the environment, and end-to-end behavior with the local model has not been verified. Unverified runtime concerns are identified in the backlog. No benchmark currently supports a capacity claim.

## 2. Backlog: Correctness

P0 = required for a reliable demo. P1 = complete the local application. P2 = support multiple users or higher load. P3 = optional extensions.

| ID | Priority | Finding and Required Action |
| --- | --- | --- |
| COR-01 | P0 | Fix `clean_llm_answer()`: isolated checks confirmed that `I don't know` becomes an empty string and `I don't know.` becomes `I`. Preserve refusal answers. |
| COR-02 | P0 | Unify configuration: `config.py` uses absolute paths and only distinguishes test mode, while the retriever uses relative paths and `data_{APP_ENV}`. |
| COR-03 | P0 | Load configuration before dependent modules; `load_dotenv()` currently runs after route imports. |
| COR-04 | P0 | Replace the APP_ENV placeholder in `.env.example` with a valid value and validate configuration at startup. |
| COR-05 | P0 | Consolidate the two pipelines: `build_prompt()` used by `RAGPipeline` treats metadata dictionaries as strings, and `generate(prompt)` differs from `generate(question, context_docs)`. RAGPipeline is not the main query path, but must still be fixed or removed. |
| COR-06 | P1 | Store the original filename in metadata instead of the UUID-based filename on disk. |
| COR-07 | P1 | Normalize the `.pdf` extension: uploads preserve `.PDF`, while downloads look for `.pdf`, which can fail on case-sensitive filesystems. |
| COR-08 | P1 | Correct the return type and docstring of `save_upload_file()` to describe its tuple; remove unused imports and dead code. |
| COR-09 | P0 | Classify query errors: invalid input as 422/400, missing documents as 404, documents not ready as 409, and dependency failures with dedicated codes instead of returning 500 for every error. |

## 3. Backlog: RAG Quality

| ID | Priority | Required Action |
| --- | --- | --- |
| RAG-01 | P1 | Consolidate chunking: the parser splits with overlap, then the service splits again by character count. Preserve page metadata and content boundaries. |
| RAG-02 | P1 | Detect scanned PDFs or PDFs without extractable text and explain the limitation; defer OCR to P3. |
| RAG-03 | P1 | Test tables, multiple columns, headers/footers, and Vietnamese text; document parser limitations. |
| RAG-04 | P1 | Refuse answers when evidence is insufficient. The query path does not currently use the helper's threshold parameter. Calibrate thresholds with evaluation data. |
| RAG-05 | P1 | Define per-file top_k and post-reranking top_n; synthesis and document-by-document comparison may need different retrieval strategies. |
| RAG-06 | P1 | Evaluate embedding, reranker, and LLM performance separately for Vietnamese; multilingual embeddings do not guarantee pipeline quality. |
| RAG-07 | P0 | Budget tokens for instructions, question, context, and output using a tokenizer compatible with the actual model. |
| RAG-08 | P1 | Fix truncate_context: do not discard all context because the first chunk exceeds the budget; truncate safely by tokens or select suitable chunks. |
| RAG-09 | P1 | Distinguish retrieved chunks from chunks actually included in the prompt; expose answer sources according to the API contract. |
| RAG-10 | P1 | Include documentId, chunkId, page, and content in citations; do not assume every retrieved chunk supports every answer claim. |
| RAG-11 | P1 | Treat document content as data rather than instructions; add PDF prompt-injection cases. |
| RAG-12 | P2 | Support multi-turn conversations with persisted history, bounded conversation context, and follow-up question resolution. |
| RAG-13 | P1 | Build an evaluation set covering answerable/unanswerable questions, Vietnamese, multiple documents, comparisons, tables, and correct/incorrect sources. Record retrieval quality, groundedness, and latency. |

## 4. Backlog: Performance and Jobs

| ID | Priority | Required Action |
| --- | --- | --- |
| PERF-01 | P0 | Manage embedding and LLM lifecycles; embedding models are currently recreated per retriever and LocalLLM per question. Bound caches and control concurrency. |
| PERF-02 | P1 | Encode each query once for indexes using the same embedding model. |
| PERF-03 | P1 | Cache indexes and metadata within a RAM limit, with invalidation on deletion or reindexing. |
| PERF-04 | P1 | Avoid downloading/loading CrossEncoder and the tokenizer during module import; expose readiness and missing-model errors at startup. |
| PERF-05 | P0 | Move synchronous parsing/embedding out of async routes using suitable offloading first, then workers. |
| PERF-06 | P2 | Use a durable indexing queue with job IDs, progress, bounded retries, timeouts, cancellation where feasible, and restart recovery. |
| PERF-07 | P0 | Stream uploads to disk in bounded blocks; limit bytes, pages, document counts, question length, top_k, and total candidates. |
| PERF-08 | P1 | Bound concurrent AI tasks and queue capacity; return clear overload responses. |
| PERF-09 | P0 | Add timeouts and network error handling to every HTTP client; retry only safe or idempotent operations. |
| PERF-10 | P2 | Stream answers through SSE when supported by the provider; handle disconnected clients. |
| PERF-11 | P1 | Measure p50/p95 latency, throughput, RAM/VRAM, and stage timings before adding workers. Multiple processes can duplicate models in RAM. |

## 5. Backlog: Data and Document Protection

| ID | Priority | Required Action |
| --- | --- | --- |
| DATA-01 | P0 | Prevent lost updates during read-modify-write operations on file_map.json; use safe writes initially and migrate metadata to a database later. |
| DATA-02 | P0 | Do not suppress mapping read errors and overwrite existing data; report errors and preserve the original. |
| DATA-03 | P0 | Write indexes/metadata to temporary locations and publish ready state only after artifacts are complete; roll back or mark failed on errors. |
| DATA-04 | P1 | Clean up orphaned files, mappings, and indexes, and reconcile interrupted jobs. |
| DATA-05 | P1 | Add document status, processing errors, and timestamps. |
| DATA-06 | P2 | Version embedding models, chunking, index formats, and pipelines; define a reindexing procedure. |
| DATA-07 | P2 | Scope checksums and deduplication to users; do not leak other users' document existence through deduplication. |
| DATA-08 | P1 | Add document list/detail/delete/reindex APIs with consistent file and artifact cleanup. |
| DATA-09 | P2 | Define backup, restore, retention, and shared storage for multiple replicas. Local directories are sufficient for the local demo. |
| SEC-01 | P2 | Enforce authentication and ownership for list/query/download/delete. UUIDs do not replace authorization. Required before a multi-account demo with private data. |
| SEC-02 | P0 | Validate UUIDs and ensure resolved paths remain within the storage root. Strings are currently joined into paths; HTTP exploitability has not been tested. |
| SEC-03 | P0 | Validate PDF contents beyond the extension, handle malformed/encrypted files, and limit parsing resources. |
| SEC-04 | P1 | Restrict CORS to configured local origins and configure credentials appropriately instead of using a wildcard. |
| SEC-05 | P2 | Add per-user rate limits and document/storage/job quotas. |
| SEC-06 | P1 | Keep internal paths and raw exceptions out of client responses; log server errors with request IDs. |
| SEC-07 | P1 | Do not return Hugging Face failures as successful answers; standardize provider errors. |
| SEC-08 | P1 | Replace pickle metadata with JSON or another suitable schema, or strictly restrict artifacts to trusted sources; never unpickle uploaded data. |
| SEC-09 | P1 | Do not commit secrets, private PDFs, or model files; document when cloud providers receive document contents. |

## 6. Backlog: React and User Experience

| ID | Priority | Required Action |
| --- | --- | --- |
| UI-01 | P1 | Persist the document library across refreshes; new uploads must not replace previous document selections. |
| UI-02 | P1 | Support selection, deselection, deletion, status display, and retries for failed documents. |
| UI-03 | P1 | Persist and display conversation history; results must survive UI rerenders. |
| UI-04 | P1 | Disable actions or explain missing inputs; show connection errors and appropriate retry controls. |
| UI-05 | P1 | Configure the API base URL; remove hardcoded localhost URLs from application logic and PDF links. |
| UI-06 | P1 | Open citations at the correct PDF page through a viewer or #page fragment; distinguish internal page indexes from displayed page numbers. |
| UI-07 | P1 | Return original filenames in responses instead of requesting them separately for each chunk. |
| UI-08 | P1 | Replace raw responses, paths, and UUIDs in user flows with names, statuses, page counts, and clear messages. |
| UI-09 | P1 | Display upload/index progress and distinguish uploading, processing, ready, and failed states. |
| UI-10 | P1 | Provide loading, empty, and error states, keyboard access, and layouts usable on small screens. |
| UI-11 | P3 | Add OCR, DOCX/TXT/Markdown, conversation export, and other extensions after the PDF workflow is stable. |

## 7. Backlog: Testing and Operations

| ID | Priority | Required Action |
| --- | --- | --- |
| TEST-01 | P0 | Replace file_id with file_ids in request and service tests. |
| TEST-02 | P0 | Match mock contexts and responses to the current dictionary schema; mock reranking in unit tests. |
| TEST-03 | P0 | Fix parser tests expecting str, index tests passing list[str], and split_text_to_docs calls missing required arguments. |
| TEST-04 | P0 | Build mock indexes with the same embedding model/version as the retriever; matching dimensions alone does not ensure compatibility. |
| TEST-05 | P0 | Require an index-building fixture in every test that needs it; do not depend on pre-existing artifacts. |
| TEST-06 | P0 | Actually mock the LLM in mock tests; separate model/network tests into an optional integration group. |
| TEST-07 | P0 | Force test configuration and temporary storage without touching demo/real data; avoid font/model downloads during test collection. |
| TEST-08 | P1 | Test upload-query-source, malformed/empty/scanned PDFs, input limits, timeouts, rollback, concurrency, and restart recovery. |
| TEST-09 | P2 | Test ownership with two users, Nest–FastAPI contracts, and critical React flows against real backends. |
| OPS-01 | P1 | Select supported Python/Node versions and verify clean installation; declare direct dependencies, use suitable lockfiles, and separate dev/test dependencies. |
| OPS-02 | P1 | Run tests without large models in CI, plus lint/typecheck and frontend/backend builds. |
| OPS-03 | P1 | Separate health and readiness checks; readiness must reflect required model/storage availability. |
| OPS-04 | P1 | Use structured logs and request/job IDs across services; do not log secrets or full documents by default. |
| OPS-05 | P1 | Align README with the implementation, configuration, parser limitations, hardware requirements, and model setup. |
| OPS-06 | P2 | Add optional Docker/Compose, migrations, backup/restore, and graceful shutdown. Kubernetes is not required. |

## 8. Target Architecture: NestJS + FastAPI + React

```text
Browser / React
       |
       v
NestJS :3000 -- PostgreSQL :5432
       |       (user, document, job, conversation, message)
       |
       +-- Local storage (PDF)
       |
       +-- Redis :6379 / queue -- Indexing orchestration worker
       |                              |
       +------------------------------+--> FastAPI :8000
                                              |
                                              +-- Parse / chunk / embed / FAISS
                                              +-- Rerank / prompt / local LLM
```

The proposed React development port is :5173. Ports are conventions, not requirements. Add the queue and worker during the background-processing phase rather than at initial setup.

### Responsibilities

| Component | Owns | Avoid |
| --- | --- | --- |
| React | Document UI, chat, progress, citations | Direct database access, secrets, or authorization decisions |
| NestJS | Public API, authentication/ownership, metadata, conversations, job orchestration, PDF downloads | Running embedding or LLM workloads inside Node processes |
| FastAPI | AI pipeline, index artifacts, AI result schemas | Trusting browser-provided userId or creating a second user-management system |
| Worker | Claiming jobs, calling AI, updating results/status according to the contract | Unlimited retries or marking ready before artifacts are complete |

For the local demo, Nest and Python can share a storage directory using server-generated relative paths. FastAPI accepts validated artifact IDs/storage keys, not arbitrary browser-supplied paths. Object storage can replace local storage when services move to separate machines without changing the UI.

Route public API calls through NestJS. FastAPI is internal: bind it to localhost for the local demo and do not call it directly from the frontend. Deployment beyond localhost requires appropriate service authentication and network controls.

### Minimum Data Model

- User: id, authentication details, timestamps; can follow the single-user workflow.
- Document: id, ownerId, originalName, storageKey, checksum, status, pageCount, errorCode, pipelineVersion, timestamps.
- ProcessingJob: id, documentId, type, status, attempts, progress, errorCode, timestamps.
- Conversation: id, ownerId, title, timestamps; associated selected documents.
- Message: id, conversationId, role, content, status, citations, timestamps.
- Index manifest: documentId, indexVersion, embedding model/revision, dimension, chunking version, artifact keys.

Nest owns application metadata. Python manages chunks/indexes and returns manifests. Avoid having both services independently control document state.

### Proposed API Contract

These routes are proposed and not implemented. IDs use UUIDs; public API pageNumber values are 1-based.

| Public Nest API | Purpose |
| --- | --- |
| POST /documents | Upload within limits and create a document/job; return 202 for background processing |
| GET /documents | Paginated list with status filtering |
| GET /documents/:id | Metadata and status |
| GET /documents/:id/content | Stream the PDF after authorization |
| DELETE /documents/:id | Delete with controlled cleanup of related jobs and artifacts |
| POST /documents/:id/reindex | Create an idempotent reindex job |
| GET /jobs/:id | Progress and user-facing errors |
| POST /conversations | Create a conversation |
| GET /conversations/:id/messages | Paginated history |
| POST /conversations/:id/messages | Submit question and documentIds; query only ready documents |

Proposed internal FastAPI endpoints: POST /internal/index, POST /internal/query, DELETE /internal/indexes/:documentId, GET /health, and GET /ready. Nest authorizes access before calling these endpoints.

Contracts need versioning, requestId/jobId, timeouts, input limits, and shared error schemas. Query results include answer, citations, usedChunkIds, and pipelineVersion. Retrieval debugging is off by default. Do not return filesystem paths.

### State and Consistency

```text
UPLOADED -> PROCESSING -> READY
                      -> FAILED -> PROCESSING (retry)
READY/FAILED -> DELETING -> deleted
```

- Accept queries only for READY documents with a published index version.
- Make jobs idempotent by documentId + pipelineVersion + operation type.
- Do not assume exactly-once queue delivery; safely handle repeated execution.
- Build a new version for reindexing, switch the manifest after completion, then clean up the old version.
- If deletion occurs during processing, check document state before publishing results.
- An HTTP timeout does not prove Python processing stopped; reconcile state before retrying.
- Reconcile interrupted jobs and temporary artifacts on worker startup.

## 9. React and a Local Demo Without Hosting

Use React + TypeScript + Vite for this demo. SSR and Next.js are not required. Choose a familiar UI library, an HTTP client with timeouts, and one server-state management approach; avoid overlapping tools.

Minimum screens:

1. Document library: upload, status, selection, deletion, retry.
2. Conversations: conversation list, messages, loading/errors, document scope selection.
3. Sources: filename, page, excerpt, and opening the PDF at the cited page.

Local operation avoids hosting/domain fees. The machine still needs sufficient RAM/CPU or GPU, model storage, and network access for initial dependency/model downloads. Do not claim offline operation until required models, tokenizers, and fonts are cached. Cloud LLM APIs may incur charges and are not the default configuration in this plan.

Target local startup procedure after implementation:

1. Install the selected Node/Python versions and prepare the local model.
2. Start PostgreSQL and, when queues are enabled, Redis through local services or Compose.
3. Run migrations and seed non-sensitive sample data.
4. Start FastAPI, NestJS, the worker if applicable, and React.
5. Open localhost:5173, upload sample PDFs, and run the demo scenario.

This is the target procedure, not an executable guide for the current repository. Retain existing Streamlit instructions until React reaches feature parity, then mark Streamlit as the legacy demo.

## 10. Implementation Roadmap and Acceptance Criteria

### Phase A — Fix the Python Foundation

Complete P0 correctness items, configuration, token budgeting, input limits, file consistency, and test contracts. Standardize one AI interface for Nest integration.

Acceptance: tests without network/large models pass; separate integration tests verify upload-query-source with the local model; malformed PDFs and unanswerable questions produce valid results; tests do not modify real data.

### Phase B — Make React + Nest the Main Workflow

Create React and Nest applications, database/migrations, document CRUD, persisted chat, authorized downloads, and internal FastAPI contracts. Implement the single-user flow first, then authentication/ownership for multi-account demos.

Acceptance: the complete demo runs from React; refresh preserves documents/conversations; browsers do not call Python directly; public APIs do not expose internal paths; users cannot access each other's documents when authentication is enabled.

### Phase C — Background Processing and Reliability

Add queue/workers, progress, retries/idempotency, model lifecycle/caching, concurrency limits, cross-service logs, and restart recovery.

Acceptance: upload requests do not wait for full indexing; failed jobs can retry; repeated jobs do not duplicate data; restarts do not leave jobs permanently processing; deletion/reindexing does not expose incomplete indexes.

### Phase D — Evaluate and Package the Demo

Add RAG evaluation, bounded local load testing, clean-start instructions, optional scripts/Compose, sample PDFs, and a demo scenario.

Acceptance: document hardware/model configuration, measured latency/RAM, and tested limits; no paid service is required; provide safe data-reset and readiness instructions.

### Phase E — Expand Only When Needed

Consider OCR/new formats, dedicated inference serving, object storage, vector databases, multiple API replicas, centralized observability, and hosting based on measurements and actual requirements.

## 11. Demo Completion Checklist

- [ ] A clean installation runs using README instructions.
- [ ] The default configuration needs no cloud secrets or paid accounts.
- [ ] Users can upload one/multiple PDFs, track progress, and query ready documents.
- [ ] Answer citations open the correct file/page.
- [ ] Unanswerable questions do not produce fabricated or empty answers.
- [ ] Malformed/scanned/oversized PDFs produce clear messages.
- [ ] Documents and conversations survive refresh/restart as designed.
- [ ] Delete/reindex/retry preserve correct states and artifacts.
- [ ] API validation, timeouts, and dependency failures are tested.
- [ ] Tests/CI and React/Nest builds pass; AI integration tests have separate instructions.
- [ ] Ownership is verified with two users when authentication is enabled.
- [ ] Measurements and actual limits are documented for the demo machine.

## 12. Architecture References

- [FastAPI deployment and per-process memory](https://fastapi.tiangolo.com/deployment/concepts/)
- [NestJS queues](https://docs.nestjs.com/techniques/queues)

These references inform implementation choices and do not replace application benchmarks. Choosing NestJS does not imply it automatically scales better than Spring or FastAPI.

## 13. Roadmap Coverage

The four product development directions are maintained here with their status, scope, and acceptance criteria. Implementation follows the priorities and phases defined above.

### Additional Document Formats

Status: PDF-only today. DOCX, TXT, and Markdown are optional Phase E extensions, tracked by UI-11. Keep scanned-PDF OCR as a separate capability.

Use format-specific parsers behind a shared chunk schema with documentId, chunkId, content, and source location. Validate actual file contents, encoding, size, and supported formats. Preserve headings or paragraph/line references when a format has no reliable page numbers; do not invent page citations.

Acceptance: each supported format has extraction fixtures, upload-query-source integration coverage, clear errors for unsupported/corrupt input, and citations that point to a meaningful source location.

### Authentication and Authorization

Status: not implemented. Phase B introduces Nest-owned authentication and ownership when enabling multiple accounts; SEC-01, SEC-05, and TEST-09 cover enforcement and verification.

Nest checks ownership for document lists, metadata, downloads, queries, deletion, reindexing, jobs, and conversations. Python remains an internal AI service. A single-user local demo can precede authentication, but must not claim multi-user isolation.

Acceptance: two-user tests demonstrate that one user cannot discover, query, download, modify, or delete the other user's resources, including by guessing IDs. Authentication failures and authorization failures have consistent API responses.

### Separate Backend, AI Service, and Frontend

Status: the current stack is FastAPI + Streamlit. Sections 8–10 define the proposed React + NestJS + FastAPI architecture and phased migration.

Keep service boundaries limited to application logic and AI processing. Introduce queue/workers in Phase C; avoid splitting every module into a microservice. All components may run on one machine without public hosting.

Acceptance: the main React workflow calls Nest, Nest invokes FastAPI through validated internal contracts, application metadata has a single owner, and timeouts/errors can be traced across services. Retire the Streamlit workflow only after feature parity.

### Cross-Document Retrieval and Search

Status: selected-document retrieval already exists. The current query flow retrieves from each selected PDF index and reranks combined candidates; this is not a completely new feature. Its quality has not been established by an end-to-end evaluation.

RAG-04, RAG-05, RAG-10, RAG-13, PERF-02, and UI-01/UI-02 cover relevance, coverage, citations, evaluation, query embedding reuse, and document selection. Phase B improves selection and persistence; Phase D measures quality. A standalone document-search screen or lexical/hybrid search is optional future scope.

Acceptance: multi-document fixtures verify relevant retrieval, document/page attribution, exclusion of unselected or unauthorized documents, and evidence from multiple files when a comparison requires it. Unrelated questions produce an explicit insufficient-evidence result. Record quality and latency as document count increases.
