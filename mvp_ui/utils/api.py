import requests

API_URL = "http://localhost:8000"

def upload_pdf(file):
    files = {"file": (file.name, file, "application/pdf")}
    return requests.post(f"{API_URL}/documents/upload", files=files)

def ask_question(query, top_k, file_ids):
    payload = {"query": query, "top_k": top_k, "file_ids": file_ids}
    return requests.post(f"{API_URL}/documents/query", json=payload)

def get_original_filename(file_id):
    response = requests.get(f"{API_URL}/documents/filename/{file_id}")
    if response.ok:
        return response.json().get("filename")
    return None
