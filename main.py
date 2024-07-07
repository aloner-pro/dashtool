from fastapi import FastAPI, Query, File, UploadFile, HTTPException
from typing import Optional, List
import sqlite3
import pandas as pd
from pydantic import BaseModel, Field
import ast

app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect('data.db')
    return conn

class UploadResponse(BaseModel):
    detail: str

@app.post("/uploadcsv/", response_model=UploadResponse)
async def upload_csv(csv_file: UploadFile = File(...)):
    df = pd.read_csv(csv_file.file)
    if 'Unnamed: 0' in df.columns:
        df.drop(columns=['Unnamed: 0'], inplace=True)
    rename_dict = {
        'Release date': 'Release_date',
        'Required age': 'Required_age',
        'DLC count': 'DLC_count',
        'About the game': 'About_the_game',
        'Supported languages': 'Supported_languages',
        'Score rank': 'Score_rank'}
    df.rename(columns=rename_dict, inplace=True)
    # Ensure the columns match the database schema
    expected_columns = [
        'AppID', 'Name', 'Release_date', 'Required_age', 'Price',
        'DLC_count', 'About_the_game', 'Supported_languages', 'Windows',
        'Mac', 'Linux', 'Positive', 'Negative', 'Score_rank',
        'Developers', 'Publishers', 'Categories', 'Genres', 'Tags'
    ]

    if not all(col in df.columns for col in expected_columns):
        missing_cols = [col for col in expected_columns if col not in df.columns]
        raise HTTPException(status_code=400, detail=f"Missing columns in CSV: {missing_cols}")

    # Convert list columns to comma-separated strings
    list_columns = ['Supported_languages', 'Categories', 'Genres', 'Tags']
    for col in list_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: ','.join(x) if isinstance(x, list) else x)

    conn = get_db_connection()
    df.to_sql('gameData', conn, if_exists='replace', index=False)
    conn.close()

    return {"detail": "File uploaded successfully"}

class GameData(BaseModel):
    AppID: int
    Name: str
    Release_date: str
    Required_age: int
    Price: float
    DLC_count: int
    About_the_game: str
    Supported_languages: List[str]
    Windows: int = Field(ge=0,le=1)
    Mac: int = Field(ge=0,le=1)
    Linux: int = Field(ge=0,le=1)
    Positive: int
    Negative: int
    Score_rank: Optional[int]
    Developers: str
    Publishers: str
    Categories: List[str]
    Genres: List[str]
    Tags: List[str]

class SearchResponse(BaseModel):
    count: int
    results: List[GameData]

@app.get("/search", response_model=SearchResponse)
def search_games(
        AppID: Optional[int] = Query(None),
        Name: Optional[str] = Query(None),
        Release_date: Optional[str] = Query(None),
        Required_age: Optional[int] = Query(None),
        Price: Optional[float] = Query(None),
        DLC_count: Optional[int] = Query(None),
        About_the_game: Optional[str] = Query(None),
        Supported_languages: Optional[str] = Query(None),
        Windows: Optional[int] = Query(None),
        Mac: Optional[int] = Query(None),
        Linux: Optional[int] = Query(None),
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
        query += " AND Name LIKE ?"
        params.append(f"%{Name}%")

    if Release_date is not None:
        query += " AND Release_date LIKE ?"
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
    rows = cursor.fetchall()
    conn.close()

    results = []

    for row in rows:
        categories = row[16].split(',') if row[16] else []
        genres = row[17].split(',') if row[17] else []
        tags = row[18].split(',') if row[18] else []

        result = GameData(
            AppID=row[0],
            Name=row[1],
            Release_date=row[2],
            Required_age=row[3],
            Price=row[4],
            DLC_count=row[5],
            About_the_game=row[6],
            Supported_languages=ast.literal_eval(row[7]),
            Windows=row[8],
            Mac=row[9],
            Linux=row[10],
            Positive=row[11],
            Negative=row[12],
            Score_rank=row[13],
            Developers=row[14] or '',
            Publishers=row[15] or '',
            Categories=categories,
            Genres=genres,
            Tags=tags,
        )

        results.append(result)

    return {"count": len(results), "results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
