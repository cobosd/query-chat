
# components
# from utils import QdrantVectorstore
from app.chain import load_agent, sql_agent
from app.fileConversion import csv_types
from app.preprocessing import csv_to_db
import shutil
import json

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
from twilio.rest import Client


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


@app.get("/goldengoal/notify")
def notify():
    from trycourier import Courier
    import psycopg2

    receiver = os.getenv('EMAIL_RECEIVER')

    # Database connection details
    db_host = os.getenv('DB_HOST')
    db_port = 5432
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASS')
    courier_api = os.getenv('COURIER_API')
    
    def connect_to_database():
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )
        return conn


    # query = """
    #     SELECT *
    #     FROM company.matches
    #     WHERE "date" = (SELECT date
    #                     FROM company.matches
    #                     WHERE "date" > CURRENT_TIMESTAMP 
    #                     ORDER BY "date" ASC
    #                     LIMIT 1);

    #     """
    query = """
            SELECT *
            FROM company.matches
            WHERE date BETWEEN CURRENT_DATE AND (CURRENT_DATE + INTERVAL '7 days')
            AND ((
                (home_team = 'FIGUEIRENSE' OR away_team = 'FIGUEIRENSE')
                AND category = 'U15'
            )
            OR (
                (home_team = 'HERCÍLIO LUZ' OR away_team = 'HERCÍLIO LUZ')
                AND category = 'U20'
            ));
        """
    connection = connect_to_database()

    cursor = connection.cursor()


    cursor.execute(query)
    res = cursor.fetchall()
    
    connection.commit()
    cursor.close()

    # print(res)
    if len(res) != 0:
        payload = []
        
        for _, row in enumerate(res):    
            payload.append({"game_nbr":  row[0], "date": datetime.strftime(row[1], '%d/%m/%Y'), "day": row[2], "time": str(row[3])[:-3], 
                            "stadium": row[4], "city": row[5], "category": row[6], "home_team": row[7], 
                            "home_score": row[8] or "", "away_team": row[9], "away_score": row[10] or ""})
            
            
        whatsapp_string = ''
        for game in payload:
            whatsapp_string += f"Categoria: {game['category']}\n"
            whatsapp_string += f"Dia: {game['day']}\n"
            whatsapp_string += f"Data: {game['date']}\n"
            whatsapp_string += f"Casa: {game['home_team']}\n"
            whatsapp_string += f"Visitante: {game['away_team']}\n"
            whatsapp_string += f"Cidade: {game['city']}\n"
            whatsapp_string += f"Estádio: {game['stadium']}\n\n"
        
                    
        account_sid = os.getenv('ACCOUNT_SID')
        auth_token = os.getenv('WHATSAPP_TOKEN')
        
        
        client = Client(account_sid, auth_token)
                        

        message = client.messages.create(
        from_='whatsapp:+'+os.getenv('FROM_NBR'),
        body=whatsapp_string,
        to='whatsapp:+'+os.getenv('PHONE_NBR')
        )
        whatsapp_string
        client = Courier(auth_token=courier_api)
        

        # SEND EMAIL MESSAGE
        resp = client.send_message(
            message={
                "to": {"email": receiver},
                "template": "8YNFZMTV8B4E4SMVCNBD8ZMNK6DJ",
                "data": {
                    "games": payload,
                },
            }
        )
        
        return {"message": "Notification sent", "response": resp}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
