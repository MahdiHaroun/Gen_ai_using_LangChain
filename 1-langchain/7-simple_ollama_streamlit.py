import os 
from dotenv import load_dotenv
load_dotenv()


os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")

from langchain_community.llms import Ollama


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


prompt = ChatPromptTemplate.from_messages(  
    [
        ("system" , "you are a helpful assistant , please respond to the user's query."),
        ("user" , "Question: {question}")
    ]
)
import streamlit as st
#streamlit
st.title("Langchain with Ollama")
input_text = st.text_input("Enter your question:")
llm = Ollama(model="gemma:2b")

output_parser = StrOutputParser()
chain = prompt | llm | output_parser

if input_text:
    response = chain.invoke({"question": input_text})
    st.write(response)


