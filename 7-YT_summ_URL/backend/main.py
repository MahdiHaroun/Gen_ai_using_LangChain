from fastapi import FastAPI 
from routers import yt  
app = FastAPI()


app.include_router(yt.router) 
