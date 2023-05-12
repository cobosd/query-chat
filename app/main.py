
# components
# from utils import QdrantVectorstore
from app.chain import load_agent, sql_agent
from app.fileConversion import csv_types
from app.preprocessing import csv_to_db
import shutil


# dependencies
from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.templating import Jinja2Templates
from datetime import datetime
from dotenv import load_dotenv
import openai
import pandas as pd
import uvicorn
import os
import csv


# Initialization
app = FastAPI()
templates = Jinja2Templates(directory="app/templates/")

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API key
openai.api_key = os.getenv('APP_OPENAI_KEY')


UPLOAD_FOLDER = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


uploaded_data_list = []
db_file_path = []
dataframe = pd.DataFrame()

# API endpoints


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Define endpoint for text completion API


@app.post('/complete')
async def complete_text(request: Request):
    # Retrieve request data
    data = await request.json()
    print(data)
    modelSelected = int(data['modelSelected'])

    # dataframe = csv_to_db(data["filename"])

    agent = sql_agent(data['filename'], modelSelected)

    try:
        if modelSelected == 1:
            print('model 1 selected')
            output = agent(data["question"])
            return {'answer': output['result']}

        elif modelSelected == 2:
            print('model 2 selected')
            output = agent.run(data["question"])
            return {'answer': output}

    except ValueError as e:
        # # HACK: https://github.com/hwchase17/langchain/issues/1358#issuecomment-1486132587
        # response = str(e)
        # if not response.startswith("Could not parse LLM output: `"):
        #     raise e
        # response = response.removeprefix(
        #     "Could not parse LLM output: `").removesuffix("`")
        return


@app.post("/uploadfile")
async def upload_csv_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        return {"error": "Invalid file format"}

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        new_file_path = csv_to_db(file_path)

    # with open(new_file_path, 'r') as db_file:
    if len(db_file_path) != 0:
        db_file_path.pop()

    db_file_path.append(new_file_path)

    return {"status": "File uploaded successfully", "path": new_file_path}


@app.get("/deletefile")
async def delete_csv_file():

    try:
        if len(db_file_path) != 0:
            os.remove(str(db_file_path[0]))
            db_file_path.pop()
            print(f"{db_file_path} successfully removed")
    except OSError as e:
        print(f"Error: {db_file_path} - {e.strerror}")

    print("DELETE?:", db_file_path)

    return {"status": "File deleted successfully"}

################################


@app.get("/processdata")
async def process_data():
    print(db_file_path)
    # Here you can access the uploaded_data list
    for row in dataframe:
        print(row)

    return {"status": "Data processed successfully"}


@app.get("/getdata")
async def get_name():

    if len(db_file_path) == 0:
        print("No file uploaded")
        return {"message": None}
    else:
        print(str(db_file_path[0]))
        return {"message": str(db_file_path[0])}


@app.get("/time")
def get_current_time():
    return {"time": datetime.now()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
