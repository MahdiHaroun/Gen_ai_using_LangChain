from fastapi import APIRouter, HTTPException, status
from schemas import ask_question, db_info
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from sqlalchemy import create_engine
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from dotenv import load_dotenv
from routers import db_setup
import os
import logging

# Load environment variables
load_dotenv()

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LLM - use the same model as in db_setup
llm = ChatGroq(groq_api_key=os.getenv("GROQ_API"), model_name="llama3-8b-8192", streaming=False)

@router.post("/ask", status_code=status.HTTP_200_OK)
async def ask_simple_question(question_data: ask_question):

    try:
        # Check if toolkit is available from db_setup
        if db_setup.toolkit is None:
            raise HTTPException(
                status_code=400, 
                detail="Database not configured. Please call /db endpoint first to set up the database connection."
            )
        
        # Use the toolkit from db_setup
        toolkit = db_setup.toolkit
        agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True
        )
        
        # Process the question using invoke method
        
        result = await agent.ainvoke({"input": question_data.question})
            
        
        
        return {
            "question": question_data.question,
            "status": "success"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in ask endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )

