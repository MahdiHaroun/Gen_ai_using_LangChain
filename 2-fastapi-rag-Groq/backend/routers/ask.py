# routers/ask_router.py
from fastapi import APIRouter, HTTPException, Depends 
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import schemas
from backend.routers import rag_state


router = APIRouter(prefix="/ask", tags=["ask"])

@router.post("/ask", response_model=schemas.AskResponse)
async def ask_question(new_question: schemas.AskRequest, db: Session = Depends(get_db)):
    if not rag_state.conversational_rag_chain:
        raise HTTPException(status_code=400, detail="RAG not initialized. Call /rag/initRAG first.")

    response = await rag_state.conversational_rag_chain.ainvoke(
        {"input": new_question.question},
        config={"configurable": {"session_id": new_question.session_id}}
    )

    # Extract context documents
    context_docs = []
    if "context" in response:
        for doc in response["context"]:
            context_docs.append(schemas.DocumentContext(
                page_content=doc.page_content,
                metadata=doc.metadata
            ))

    return schemas.AskResponse(answer=response["answer"], context=context_docs)
