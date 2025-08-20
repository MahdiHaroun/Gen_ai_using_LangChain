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

    try:
        response = rag_state.conversational_rag_chain.invoke(
            {"input": new_question.question},
            config={"configurable": {"session_id": new_question.session_id}}
        )

        # Extract context documents if available
        context_docs = []
        if "context" in response:
            for doc in response["context"]:
                context_docs.append(schemas.DocumentContext(
                    page_content=doc.page_content,
                    metadata=doc.metadata
                ))

        # For agent-based responses, use "output" key instead of "answer"
        answer = response.get("output", response.get("answer", "No response generated"))
        
        return schemas.AskResponse(answer=answer, context=context_docs)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")
