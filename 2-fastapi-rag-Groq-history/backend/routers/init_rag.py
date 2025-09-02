# routers/rag_router.py
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
import tempfile, os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from database import get_db
from routers import rag_state

router = APIRouter(prefix="/rag", tags=["rag"])

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})

@router.post("/initRAG")
async def init_rag(api_key: str = Form(...), uploaded_files: list[UploadFile] = File(...), db: Session = Depends(get_db)):

    rag_state.llm = ChatGroq(groq_api_key=api_key, model_name="Gemma2-9b-It")

    # Load PDFs
    documents = []
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await uploaded_file.read())
            tmp_path = tmp.name
        loader = PyPDFLoader(tmp_path)
        documents.extend(loader.load())
        os.unlink(tmp_path)

    # Build vectorstore
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
    splits = text_splitter.split_documents(documents)
    rag_state.vectorstore = FAISS.from_documents(splits, embeddings)
    retriever = rag_state.vectorstore.as_retriever()

    # History-aware retriever
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", "Reformulate question based on chat history if needed."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    history_aware_retriever = create_history_aware_retriever(rag_state.llm, retriever, contextualize_q_prompt)

    # QA chain
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer concisely using the context.\n\n{context}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    question_answer_chain = create_stuff_documents_chain(rag_state.llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    rag_state.conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain, rag_state.get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )

    return {"status": "RAG initialized"}
