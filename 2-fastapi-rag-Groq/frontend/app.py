import streamlit as st
import requests

API_URL = "http://localhost:8000"  # change if deployed

st.title("RAG Chatbot")

# Step 1: Initialize RAG
st.header("1️⃣ Initialize RAG with PDFs")

with st.form("init_rag_form"):
    api_key = st.text_input("Groq API Key")
    uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)
    submit_init = st.form_submit_button("Initialize RAG")

if submit_init:
    if api_key and uploaded_files:
        files = [("uploaded_files", (f.name, f, "application/pdf")) for f in uploaded_files]
        data = {"api_key": api_key}
        response = requests.post(f"{API_URL}/rag/initRAG", data=data, files=files)
        if response.status_code == 200:
            st.success("✅ RAG initialized successfully!")
        else:
            st.error(f"❌ {response.text}")
    else:
        st.warning("Please provide API key and upload at least one PDF.")

# Step 2: Ask Questions
st.header("2️⃣ Ask Questions")
question = st.text_input("Your question")
session_id = st.text_input("Session ID (any string to identify user session)")

if st.button("Ask"):
    if question and session_id:
        payload = {"question": question, "session_id": session_id}
        response = requests.post(f"{API_URL}/ask/ask", json=payload)
        if response.status_code == 200:
            result = response.json()
            answer = result["answer"]
            context = result.get("context", [])
            
            st.info(f"💬 Answer: {answer}")
            
            # Display context documents
            if context:
                with st.expander("Show Context"):
                    for i, doc in enumerate(context):
                        st.write(f"**Document {i+1}:**")
                        st.write(doc["page_content"])
                        if doc.get("metadata"):
                            st.write(f"*Metadata: {doc['metadata']}*")
                        st.write("---")
        else:
            st.error(f"❌ {response.text}")
    else:
        st.warning("Please provide both question and session ID.")
