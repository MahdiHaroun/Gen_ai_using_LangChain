# routers/init_rag.py
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
import tempfile, os

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchRun
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool

from backend.database import get_db
from backend.routers import rag_state

router = APIRouter(prefix="/rag", tags=["rag"])

# embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})

# External tools
arxiv_wrapper = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=200)
arxiv = ArxivQueryRun(api_wrapper=arxiv_wrapper)

wiki_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)
wiki = WikipediaQueryRun(api_wrapper=wiki_wrapper)

search = DuckDuckGoSearchRun(name="Search")

@router.post("/initRAG")
async def init_rag(api_key: str = Form(...), uploaded_files: list[UploadFile] = File(default=[]), db: Session = Depends(get_db)):

    # Set up LLM
    rag_state.llm = ChatGroq(groq_api_key=api_key, model_name="Gemma2-9b-It")

    # Initialize tools list with external search tools
    tools = [search, arxiv, wiki]

    # Load PDFs only if files are provided
    if uploaded_files and len(uploaded_files) > 0:
        documents = []
        for uploaded_file in uploaded_files:
            if uploaded_file.filename:  # Check if file actually exists
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(await uploaded_file.read())
                    tmp_path = tmp.name
                loader = PyPDFLoader(tmp_path)
                documents.extend(loader.load())
                os.unlink(tmp_path)

        if documents:  # Only create RAG if we have documents
            # Vectorstore
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
            splits = text_splitter.split_documents(documents)
            rag_state.vectorstore = FAISS.from_documents(splits, embeddings)
            retriever = rag_state.vectorstore.as_retriever()

            # Simple RAG function without chat history for use as a tool
            def rag_search(query: str) -> str:
                """Search through uploaded PDF documents"""
                try:
                    docs = retriever.get_relevant_documents(query)
                    if docs:
                        context = "\n\n".join([doc.page_content for doc in docs[:3]])
                        # Use LLM to generate answer based on context
                        prompt = f"Based on the following context, answer the question: {query}\n\nContext:\n{context}"
                        response = rag_state.llm.invoke(prompt)
                        return response.content
                    return "No relevant information found in the documents."
                except Exception as e:
                    return f"Error searching documents: {str(e)}"

            # Create RAG tool
            rag_tool = Tool(
                name="LocalPDFs",
                func=rag_search,
                description="Search through uploaded PDF documents for relevant information"
            )
            
            # Add RAG tool to the beginning of tools list
            tools.insert(0, rag_tool)

    # --- Conversational Agent with memory ---
    search_agent = initialize_agent(
        tools=tools,
        llm=rag_state.llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        handle_parsing_errors=True,
        verbose=True
    )

    rag_state.conversational_rag_chain = RunnableWithMessageHistory(
        search_agent,
        rag_state.get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="output"
    )

    return {"status": "RAG initialized successfully"}
