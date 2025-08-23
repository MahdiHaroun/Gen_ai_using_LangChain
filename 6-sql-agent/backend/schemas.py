from pydantic import BaseModel

class db_info(BaseModel): 
    postgres_host : str
    postgres_port : int
    postgres_user : str
    postgres_password : str
    postgres_db : str

class ask_question(BaseModel):
    question: str




    