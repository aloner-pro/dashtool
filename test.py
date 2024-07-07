import pandas as pd
from fastapi import FastAPI, File, UploadFile
import sqlite3

app = FastAPI()
connection = sqlite3.connect('data.db')
cursor = connection.cursor()
query = f"SELECT COUNT(*) FROM gameData"


@app.get('/')
async def root():
    return {"text": "Hello"}


@app.post("/uploadcsv/")
async def upload_csv(csv_file: UploadFile = File(...)):
    df = pd.read_csv(csv_file.file)
    print(df.head())
    df = df.drop(columns=['Unnamed: 0'])
    df.to_sql('gameData', connection, if_exists='replace')
    cursor.execute(query)
    result = cursor.fetchone()
    if df.shape[0] == result[0]:
        return {"Success"}
    else:
        return {"Failed"}

