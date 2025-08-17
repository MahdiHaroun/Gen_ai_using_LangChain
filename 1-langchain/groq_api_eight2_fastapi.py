from fastapi import FastAPI
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

model = ChatGroq(model="gemma2-9b-it", api_key=os.getenv("GROQ_API"))


class groqRequest(BaseModel):
    text: str
    language: str

class groqResponse(BaseModel):
    translated_text: str

@app.post("/", response_model=groqResponse)
async def translation(new_translation: groqRequest):
    prompt_template = ChatPromptTemplate.from_messages([
        ('system', "Translate the following from english to {language}"),
        ('user', '{text}')
    ])
    parser = StrOutputParser()
    chain = prompt_template | model | parser

    response = await chain.ainvoke({
        "text": new_translation.text,
        "language": new_translation.language
    })

    return groqResponse(translated_text=response)
