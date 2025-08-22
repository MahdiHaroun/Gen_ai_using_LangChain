from fastapi import APIRouter, status 
from langchain_groq import ChatGroq
from backend.schemas import SummaryRequest, SummaryResponse
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.schema import Document
import os 


from dotenv import load_dotenv
load_dotenv()
os.environ["GROQ_API"] = os.getenv("GROQ_API")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")

router = APIRouter(prefix="/summarizing", tags=["summarizing"])

# prompts 
map_prompt_template = '''
Please summarize the following text:
{text}
SUMMARY:
'''

refine_prompt_template = '''
Your job is to produce a final summary.
We have provided an existing summary up to a certain point: {existing_answer}

We have the opportunity to refine the existing summary (only if needed) with some more context below.
------------
{text}
------------

Given the new context, refine the original summary. If the context isn't useful, return the original summary.
Add a Motivation title, start the precise summary with an introduction and provide the summary in numbered points.
REFINED SUMMARY:
'''


@router.post("/summarize_text", response_model=SummaryResponse , status_code=status.HTTP_200_OK)
async def summarize_text(new_summ: SummaryRequest):
    llm = ChatGroq(groq_api_key=new_summ.api_key, model="openai/gpt-oss-20b")

    # Wrap text in Document, then split
    docs = [Document(page_content=new_summ.text)]
    text_chunks = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    ).split_documents(docs)

    # Create PromptTemplate objects
    map_prompt = PromptTemplate(input_variables=["text"], template=map_prompt_template)
    refine_prompt = PromptTemplate(input_variables=["text", "existing_answer"], template=refine_prompt_template)

    # Refine chain
    chain = load_summarize_chain(
        llm=llm,
        chain_type="refine",
        question_prompt=map_prompt,
        refine_prompt=refine_prompt,
        verbose=True
    )

    # Run summarization
    result = await chain.ainvoke(text_chunks , return_only_outputs=True)
    
    summary_text = result['output_text']


    return SummaryResponse(summary=summary_text)
