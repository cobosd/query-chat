from langchain.llms import OpenAI
# from langchain.chains import ChatVectorDBChain
from langchain.chains.chat_vector_db.prompts import (CONDENSE_QUESTION_PROMPT, QA_PROMPT)
import os
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains import ConversationalRetrievalChain
from langchain.agents import create_csv_agent, create_pandas_dataframe_agent
from langchain.llms import OpenAI

def load_agent(file):
    """Contruct a chat chain to query vectorstore and return the answer. This already includes chat memory and streaming callback""" 
    openai_api_key = os.environ['OPENAI_API_KEY']
    
    # agent = create_csv_agent(OpenAI(temperature=0), file, verbose=True)
    agent = create_pandas_dataframe_agent(OpenAI(temperature=0), file, verbose=True)
    
    return agent