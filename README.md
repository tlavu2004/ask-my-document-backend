# Ask My Document - Backend MVP

Ứng dụng hỏi đáp tài liệu PDF sử dụng **RAG (Retrieval Augmented Generation)** và **LLM local** (.bin).  
Người dùng có thể upload tài liệu PDF, hệ thống sẽ trích xuất dữ liệu, lưu vào FAISS và trả lời câu hỏi dựa trên nội dung tài liệu.

---

## 🚀 Cài đặt

```bash
# Clone dự án
git clone https://github.com/TTDATN-QTV/ask-my-document-backend.git
cd ask-my-document-backend

# Tạo virtual environment
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate

# Cập nhật pip và cài đặt dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## ⚡️ Chạy Backend (FastAPI)

```bash
uvicorn app.main:app --reload
```

Truy cập API docs tại: http://127.0.0.1:8000/docs

## 🖥️ Chạy giao diện MVP (Streamlit)

```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate
python -m streamlit run mvp_ui/main.py
```

## 📥 Tải LLM và dữ liệu mẫu
- Tải LLM (GGML .bin): `https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/tree/main`
- Tải file PDF mẫu: `https://drive.google.com/drive/folders/1_0JWnoLTJsbmswUGs5z1ULd7u4fqfzEf?usp=drive_link`

## 🔀 Đổi LLM khác
Khi muốn đổi sang LLM khác:
- Tải GGML .bin về vè đặt trong thư ục models/ tại thư mục gốc.
- Thay `model_path` trong file `app/utils/llm_client.py`

```python
# Existing code...

class LocalLLM:
    def __init__(self, model_path="models/llama-2-7b-chat.ggmlv3.q4_1.bin"): # <-- Thay model_path tại đây
        self.llm = CTransformers(
            model=model_path,
            model_type="llama",
            config={
                "max_new_tokens": 256,
                "temperature": 0.01
            }
        )

# Existing code...
```


## 📂 Cấu trúc thư mục
```
ask-my-document-backend/
├── app/
│   ├── rag/
│   │   ├── retriever.py
│   │   └── rag_pipeline.py
│   ├── routes/
│   │   ├── upload.py
│   │   └── query.py
│   ├── services/
│   │   ├── document_service.py
│   │   └── chat_service.py
│   ├── utils/
│   │   ├── pdf_parser.py
│   │   └── llm_client.py
│   ├── config.py
│   └── main.py
│
├── data/
│   ├── uploads/
│   └── index/
│
├── fonts/
│
├── scripts/
│   └── llama-2-7b-chat.ggmlv3.q4_1.bin
│
├── mvp_ui/
│   ├── main.py
│   ├── components/
│   └── utils/
│
├── scripts/
│   └── make_sample_pdf.py
│
├── tests/
│   ├── rag/
│   │   ├── test_rag_pipeline.py
│   │   └── test_retriever.py
│   ├── resources/
│   │   └── sample.pdf
│   ├── routes/
│   │   ├── test_upload.py
│   │   └── test_query.py
│   ├── services/
│   │   ├── test_document_service.py
│   │   └── test_chat_service.py
│   ├── utils/
│   │   ├── build_mock_index.py
│   │   └── test_llm_client.py
│   └── conftest.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

## ✨ Chức năng

- 📄 Upload tài liệu PDF.
- 🔎 Tách văn bản, chia nhỏ theo đoạn.
- 📦 Lưu embedding vào FAISS để truy vấn nhanh.
- 💬 Hỏi đáp với LLM local (sử dụng mô hình .bin).
- 🌐 REST API (FastAPI) + Giao diện MVP (Streamlit).
- ⚙️ Hỗ trợ nhiều tài liệu, metadata theo dõi context.
- 🚀 Dễ mở rộng sang Hugging Face API hoặc LLM khác.

## 🔮 Định hướng phát triển

- Hỗ trợ nhiều định dạng tài liệu (DOCX, TXT, Markdown).
- Tích hợp xác thực người dùng & phân quyền.
- Tích hợp microservice + frontend riêng biệt.
- Thêm chức năng tìm kiếm đa tài liệu.
