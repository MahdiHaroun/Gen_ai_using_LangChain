# Global state management for RAG
from langchain_community.chat_message_histories import ChatMessageHistory

# Global variables to store RAG components
llm = None
vectorstore = None
conversational_rag_chain = None

# Session history store
store = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]
