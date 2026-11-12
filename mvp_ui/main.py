import streamlit as st
from mvp_ui.utils.api import upload_pdf, ask_question, get_original_filename

st.set_page_config(page_title="Ask My Document", layout="wide")
st.title("Ask My Document")

# --- Upload PDF ---
st.header("1. Upload PDF")
uploaded_files = st.file_uploader("Choose PDF files", type=["pdf"], accept_multiple_files=True)
file_ids = st.session_state.get("file_ids", [])

if uploaded_files:
    if st.button("Upload PDFs"):
        new_file_ids = []
        for uploaded_file in uploaded_files:
            with st.spinner(f"Uploading {uploaded_file.name}..."):
                response = upload_pdf(uploaded_file)
            if response.ok:
                data = response.json()
                st.success(f"Uploaded {uploaded_file.name}!")
                st.write(data)
                file_id = data.get("file_id")
                if file_id:
                    new_file_ids.append(file_id)
            else:
                st.error(response.text)

        # Save the new file IDs to session
        st.session_state["file_ids"] = new_file_ids
        file_ids = new_file_ids

# --- Ask a question ---
st.header("2. Ask a question")
query = st.text_input("Your question:")
top_k = st.number_input("Top K context chunks", min_value=1, max_value=10, value=2)
file_ids_input = st.session_state.get("file_ids", [])

st.write(f"Current file IDs: {file_ids_input}")

if st.button("Ask") and query and file_ids_input:
    with st.spinner("Getting answer..."):
        response = ask_question(query, top_k, file_ids_input)
    if response.ok:
        result = response.json()
        st.subheader("Answer")
        st.write(result.get("answer", "No answer"))
        st.subheader("Context")
        context_chunks = result.get("context", [])
        for chunk in context_chunks:
            # Get original file name from API
            original_name = get_original_filename(chunk['file_id']) or chunk['file_name']
            st.markdown(f"**File:** {original_name} | **Page:** {chunk['page_number'] + 1}")
            st.write(chunk['content'])
            pdf_url = f"http://localhost:8000/documents/pdf/{chunk['file_id']}"
            st.markdown(
                f"[Open PDF at {original_name} (page {chunk['page_number'] + 1})]({pdf_url})",
                unsafe_allow_html=True
            )
    else:
        st.error(response.text)
