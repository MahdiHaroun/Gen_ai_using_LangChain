
import os 
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain 
from langchain_groq import ChatGroq 
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import streamlit as st  


load_dotenv()

os.environ["GROQ_API"] = os.getenv("GROQ_API")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")
os.environ["HF_TOKEN"] = os.getenv("HF_Token")

app = FastAPI()

llm=ChatGroq(groq_api_key=os.getenv("GROQ_API"),model="openai/gpt-oss-20b")
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)
prompt = ChatPromptTemplate.from_messages([
    '''
Answer the questions based on the provided context only.
please provide the most accurate response depends on the question.
before genrating the response startign the text with " depending on the context provided".
give the genrated text literaly fom the context
give
<context>
{context}
</context>
Question:{input}

'''

])

def create_vector_embedding():
    if "vectors" not in st.session_state:
        st.session_state.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )
        st.session_state.loader = PyPDFDirectoryLoader("research_papers")
        st.session_state.docs = st.session_state.loader.load()
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs)
        st.session_state.vectorstore = FAISS.from_documents(
            st.session_state.final_documents,
            st.session_state.embeddings
        )

user_prompt = st.text_input ("enter your query from the reseach paper")
if st.button("Search"):
    create_vector_embedding()
    st.success("Vector embeddings created successfully!")

import time 
from langchain.chains.retrieval import create_retrieval_chain
if user_prompt:
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = st.session_state.vectorstore.as_retriever()
    retriever_chain = create_retrieval_chain(retriever, document_chain)

    start = time.process_time()
    response = retriever_chain.invoke({"input": user_prompt})
    print(f"Response time : {time.process_time() - start}")
    st.write(response["answer"])


    with st.expander("Show Context"):
        for i , doc in enumerate(response["context"]):
            st.write(f"Document {i}: {doc.page_content}")
            st.write("---") 