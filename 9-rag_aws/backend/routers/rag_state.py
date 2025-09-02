from langchain_community.chat_message_histories import ChatMessageHistory

vectorstore = None
conversational_rag_chain = None
session_store = {}
llm = None

def get_session_history(session_id: str):
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]
