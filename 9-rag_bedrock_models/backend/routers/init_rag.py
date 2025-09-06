# routers/rag_router.py
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
import tempfile, os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.embeddings import BedrockEmbeddings 
import numpy as np 
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate   
from langchain.chains import RetrievalQA 

from database import get_db
from routers import rag_state
import boto3

#bedrock clinets 
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')


embeddings = BedrockEmbeddings(model_id = "amazon.titan-embed-text-v1", client=bedrock_runtime)





router = APIRouter(prefix="/rag", tags=["rag"])
# bedrock embedding 


@router.post("/initRAG")
async def init_rag(uploaded_files: list[UploadFile] = File(...)):

    rag_state.llm = Bedrock(
        model_id="meta.llama3-8b-instruct-v1:0", 
        client=bedrock_runtime, 
        model_kwargs={
            "temperature": 0.01, 
            "max_gen_len": 100
        },
        streaming=True
    )

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
