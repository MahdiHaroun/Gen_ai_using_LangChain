from fastapi import FastAPI 
import models 
from database import engine  
from routers import init_rag, ask 





models.Base.metadata.create_all(bind=engine)  # Create tables in the database


app = FastAPI()

app.include_router(init_rag.router)  
app.include_router(ask.router)  


@app.get("/")  # Root endpoint
def root():
    return {"message": "api-groq"}