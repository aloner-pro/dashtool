# Dashtool
API to upload csv file **(following game_data schema)** and query it based on filters.

## /uploadcsv
See Example_game_data.csv for the expected schema of the csv.\
On successful upload we get
```
{
  "detail": "File uploaded successfully"
}
```
## /search
The output schema is 
```
{
  "count": 0,
  "results": [
    {
      "AppID": 0,
      "Name": "string",
      "Release_date": "string",
      "Required_age": 0,
      "Price": 0,
      "DLC_count": 0,
      "About_the_game": "string",
      "Supported_languages": [
        "string"
      ],
      "Windows": 0,
      "Mac": 0,
      "Linux": 0,
      "Positive": 0,
      "Negative": 0,
      "Score_rank": 0,
      "Developers": "string",
      "Publishers": "string",
      "Categories": [
        "string"
      ],
      "Genres": [
        "string"
      ],
      "Tags": [
        "string"
      ]
    }
  ]
}
```
count: Num of rows that match the query\
results: A list of all the rows that match the query

## Docker image 
The image size if of 459 MB

## Deployed FastAPI on Render
Deployed on Render through Docker image from Dockerhub with public repo devsohel/dashtool\
[Deployed link](https://dashtool.onrender.com/docs)

## Features to add
TODO
- authentication
- aggregate search
- mean/min/max query support for numeric columns
- CI/CD
- Writing unit tests
