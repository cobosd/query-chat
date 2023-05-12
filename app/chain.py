from langchain.llms import OpenAI
# from langchain.chains import ChatVectorDBChain
from langchain.chains.chat_vector_db.prompts import (
    CONDENSE_QUESTION_PROMPT, QA_PROMPT)
import os
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain,  SQLDatabaseChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains import ConversationalRetrievalChain
from langchain.agents import create_csv_agent, create_pandas_dataframe_agent
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.agents import AgentExecutor
from langchain.llms import OpenAI
from dotenv import load_dotenv


def load_agent(file):
    """Contruct a chat chain to query vectorstore and return the answer. This already includes chat memory and streaming callback"""

    # Load environment variables from .env file
    load_dotenv()
    # Initialize OpenAI API key
    api_key = os.getenv('APP_OPENAI_KEY')

    # agent = create_csv_agent(OpenAI(temperature=0), file, verbose=True)
    agent = create_pandas_dataframe_agent(
        OpenAI(temperature=0, openai_api_key=api_key), file, verbose=True)

    return agent


def sql_agent(file_path, model):

    file_name = file_path.split('/')[-1]
    print(f"sqlite:///app/uploads/{file_name}")
    # Load environment variables from .env file
    load_dotenv()

    # Initialize OpenAI API key
    api_key = os.getenv('APP_OPENAI_KEY')
    print("API KEY IS:", api_key)

    llm = OpenAI(temperature=0, openai_api_key=api_key,
                 model_name="gpt-3.5-turbo")

    print("OPENAI HAS BEEN INITIALIZED")

    db = SQLDatabase.from_uri(f"sqlite:///app/uploads/{file_name}")

    toolkit = SQLDatabaseToolkit(db=db, llm=llm, verbose=True)

    if model == 1:
        print("running 1")
        sql_executor = SQLDatabaseChain(
            llm=llm, database=db, verbose=True, return_intermediate_steps=True)

    elif model == 2:
        print("running 2")

        sql_executor = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True
        )

    return sql_executor
