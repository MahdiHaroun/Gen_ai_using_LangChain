from fastapi import APIRouter, status , HTTPException 
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from schemas import db_info 
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from sqlalchemy import create_engine
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType

import os 
load_dotenv()
os.environ["GROQ_API"] = os.getenv("GROQ_API")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")

router = APIRouter()

llm=ChatGroq(groq_api_key=os.getenv("GROQ_API"),model_name="llama3-8b-8192",streaming=False)

# Global variables to store toolkit and db
toolkit = None
db = None
    

@router.post("/db" , status_code=status.HTTP_201_CREATED) 
async def sql_agent(new_db_info: db_info):
    global toolkit, db
    
    db = SQLDatabase(create_engine(f"postgresql://{new_db_info.postgres_user}:{new_db_info.postgres_password}@{new_db_info.postgres_host}/{new_db_info.postgres_db}"))
    if db:
        toolkit=SQLDatabaseToolkit(db=db,llm=llm)
        return {
            "message": "Database connection established successfully",
            "database": new_db_info.postgres_db
        }
    else:
        raise HTTPException(status_code=404, detail="Database configuration failed")
    
    


