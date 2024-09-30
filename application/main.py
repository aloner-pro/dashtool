from fastapi import FastAPI, Query, File, UploadFile, HTTPException, Depends, Response, status
from fastapi.security import HTTPBearer
from typing import Optional, Union
from .utils import VerifyToken
from .model import SearchResponse, ErrorResponse, GameData, UploadResponse
import sqlite3
import pandas as pd
import ast

app = FastAPI()
token_auth_scheme = HTTPBearer()

def get_db_connection():
    conn = sqlite3.connect('data.db')
    return conn

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

    conn = get_db_connection()
    df.to_sql('gameData', conn, if_exists='replace', index=False)
    conn.close()

    return {"detail": "File uploaded successfully"}


# Dependency function to validate GameData
def validate_game_data(game_data: GameData):
    if not (game_data.Windows in [0, 1] and game_data.Mac in [0, 1] and game_data.Linux in [0, 1]):
        raise HTTPException(status_code=400, detail="Invalid OS support values")
    return game_data

@app.get("/search", response_model=Union[SearchResponse, ErrorResponse])
async def search_games(
        response: Response,
        token: str = Depends(token_auth_scheme),
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
        Tags: Optional[str] = Query(None),
        conn: sqlite3.Connection = Depends(get_db_connection)
):

    token_result = VerifyToken(token.credentials).verify()
    if token_result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=token_result.get("msg", "Invalid token"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM gameData WHERE 1=1"
    params = []
    if AppID:
        query += " AND AppID = ?"
        params.append(AppID)

    if Name:
        query += " AND Name LIKE ?"
        params.append(f"%{Name}%")

    if Release_date:
        query += " AND Release_date LIKE ?"
        params.append(f"%{Release_date}%")

    if Required_age:
        query += " AND Required_age = ?"
        params.append(Required_age)

    if Price:
        query += " AND Price = ?"
        params.append(Price)

    if DLC_count:
        query += " AND DLC_count = ?"
        params.append(DLC_count)

    if About_the_game:
        query += " AND About_the_game LIKE ?"
        params.append(f"%{About_the_game}%")

    if Supported_languages:
        query += " AND Supported_languages LIKE ?"
        params.append(f"%{Supported_languages}%")

    if Windows:
        query += " AND Windows = ?"
        params.append(Windows)

    if Mac:
        query += " AND Mac = ?"
        params.append(Mac)

    if Linux:
        query += " AND Linux = ?"
        params.append(Linux)

    if Positive:
        query += " AND Positive = ?"
        params.append(Positive)

    if Negative:
        query += " AND Negative = ?"
        params.append(Negative)

    if Score_rank:
        query += " AND Score_rank = ?"
        params.append(Score_rank)

    if Developers:
        query += " AND Developers LIKE ?"
        params.append(f"%{Developers}%")

    if Publishers:
        query += " AND Publishers LIKE ?"
        params.append(f"%{Publishers}%")

    if Categories:
        query += " AND Categories LIKE ?"
        params.append(f"%{Categories}%")

    if Genres:
        query += " AND Genres LIKE ?"
        params.append(f"%{Genres}%")

    if Tags:
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
