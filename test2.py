from fastapi import FastAPI, Query, File, UploadFile
from typing import Optional, List
import sqlite3
import pandas as pd

app = FastAPI()


def get_db_connection():
    conn = sqlite3.connect('data.db')
    return conn

@app.post("/uploadcsv/")
async def upload_csv(csv_file: UploadFile = File(...)):
    df = pd.read_csv(csv_file.file)
    df.drop(columns=['Unnamed: 0'], inplace=True)
    rename_dict = {'Release date': 'Release_date',
                   'Required age': 'Required_age',
                   'DLC count': 'DLC_count',
                   'About the game': 'About_the_game',
                   'Supported languages' : 'Supported_languages',
                   'Score rank': 'Score_rank'}
    df.rename(columns=rename_dict, inplace=True)
    connection = get_db_connection()
    cursor = connection.cursor()
    df.to_sql('gameData', connection, if_exists='replace')
    query = f"SELECT COUNT(*) FROM gameData"
    cursor.execute(query)
    result = cursor.fetchone()
    if df.shape[0] == result[0]:
        return {"Success"}
    else:
        return {"Failed"}

@app.get("/search")
def search_games(
        AppID: Optional[int] = Query(None),
        Name: Optional[str] = Query(None),
        Release_date: Optional[str] = Query(None),
        Required_age: Optional[int] = Query(None),
        Price: Optional[float] = Query(None),
        DLC_count: Optional[int] = Query(None),
        About_the_game: Optional[str] = Query(None),
        Supported_languages: Optional[str] = Query(None),
        Windows: Optional[bool] = Query(None),
        Mac: Optional[bool] = Query(None),
        Linux: Optional[bool] = Query(None),
        Positive: Optional[int] = Query(None),
        Negative: Optional[int] = Query(None),
        Score_rank: Optional[int] = Query(None),
        Developers: Optional[str] = Query(None),
        Publishers: Optional[str] = Query(None),
        Categories: Optional[str] = Query(None),
        Genres: Optional[str] = Query(None),
        Tags: Optional[str] = Query(None)
):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM gameData WHERE 1=1"
    params = []

    if AppID is not None:
        query += " AND AppID = ?"
        params.append(AppID)
    if Name is not None:
        query += " AND Name LIKE ? "
        params.append(f"%{Name}%")
    if Release_date is not None:
        query += " AND Release_date LIKE ? "
        params.append(f"%{Release_date}%")
    if Required_age is not None:
        query += " AND Required_age = ?"
        params.append(Required_age)
    if Price is not None:
        query += " AND Price = ?"
        params.append(Price)
    if DLC_count is not None:
        query += " AND DLC_count = ?"
        params.append(DLC_count)
    if About_the_game is not None:
        query += " AND About_the_game LIKE ?"
        params.append(f"%{About_the_game}%")
    if Supported_languages is not None:
        query += " AND Supported_languages LIKE ?"
        params.append(f"%{Supported_languages}%")
    if Windows is not None:
        query += " AND Windows = ?"
        params.append(Windows)
    if Mac is not None:
        query += " AND Mac = ?"
        params.append(Mac)
    if Linux is not None:
        query += " AND Linux = ?"
        params.append(Linux)
    if Positive is not None:
        query += " AND Positive = ?"
        params.append(Positive)
    if Negative is not None:
        query += " AND Negative = ?"
        params.append(Negative)
    if Score_rank is not None:
        query += " AND Score_rank = ?"
        params.append(Score_rank)
    if Developers is not None:
        query += " AND Developers LIKE ?"
        params.append(f"%{Developers}%")
    if Publishers is not None:
        query += " AND Publishers LIKE ?"
        params.append(f"%{Publishers}%")
    if Categories is not None:
        query += " AND Categories LIKE ?"
        params.append(f"%{Categories}%")
    if Genres is not None:
        query += " AND Genres LIKE ?"
        params.append(f"%{Genres}%")
    if Tags is not None:
        query += " AND Tags LIKE ?"
        params.append(f"%{Tags}%")

    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()
    count = len(results)
    return {"count": count, "results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
