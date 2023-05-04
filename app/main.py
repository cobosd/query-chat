
# components
# from utils import QdrantVectorstore
from app.chain import load_agent
from app.fileConversion import csv_types
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
csv_file_path = []
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

    dataframe = csv_types(data["filename"])

    agent = load_agent(dataframe)

    output = agent.run(data["question"])

    return {'answer': output}


@app.post("/uploadfile")
async def upload_csv_file(file: UploadFile = File(...)):
    print('FILE:', file)

    if not file.filename.endswith('.csv'):
        return {"error": "Invalid file format"}

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        if len(csv_file_path) != 0:
            csv_file_path.pop()

        csv_file_path.append(file_path)

        for row in csv_reader:
            uploaded_data_list.append(row)

    return {"status": "File uploaded successfully"}


@app.get("/deletefile")
async def delete_csv_file():

    try:
        if len(csv_file_path) != 0:
            os.remove(str(csv_file_path[0]))
            csv_file_path.pop()
            print(f"{csv_file_path} successfully removed")
    except OSError as e:
        print(f"Error: {csv_file_path} - {e.strerror}")

    print("DELETE?:", csv_file_path)

    return {"status": "File deleted successfully"}


@app.get("/processdata")
async def process_data():
    print(csv_file_path)
    # Here you can access the uploaded_data list
    for row in dataframe:
        print(row)

    return {"status": "Data processed successfully"}


@app.get("/getdata")
async def get_name():

    if len(csv_file_path) == 0:
        print("No file uploaded")
        return {"message": None}
    else:
        print(str(csv_file_path[0]))
        return {"message": str(csv_file_path[0])}


@app.get("/time")
def get_current_time():
    return {"time": datetime.now()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
