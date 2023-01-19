from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional


class Movie(BaseModel):
    id: Optional[int] = None
    name: str = Field(default="No name", max_length=100, min_length=1)
    year: int = Field(default=2020, ge=1900, le=2023)
    overview: str = Field(default="No overview", max_length=1000, min_length=5)
    rating: float = Field(default=0.0, ge=0.0, le=10.0)
    category: str = Field(default="No category", max_length=100, min_length=1)

    class Config():
        schema_extra = {
            "example": {
                "id": 5,
                "name": "The Matrix",
                "year": 1999,
                "overview": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
                "rating": 8.7,
                'category': 'Acción'
            }
        }


app = FastAPI()
app.title = "Movies API"
app.version = "0.0.1"

movies = [
    {
        "id": 1,
        "name": "The Matrix",
        "year": 1999,
        "overview": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
        "rating": 8.7,
        'category': 'Acción'
    },
    {
        "id": 2,
        "name": "Blanca nieves",
        "year": 1949,
        "overview": "Una mujer con 7 hombres en el bosque.",
        "rating": 8.7,
        'category': 'Ficción'
    },
]


@app.get("/", tags=["movies"])
def get_movies():
    return movies


@app.get("/movies/{id}", tags=["movies"])
def get_movies(id: int):
    for movie in movies:
        if movie['id'] == id:
            return movie
    return {"error": "Movie not found"}


@app.get("/movies/category/", tags=["movies"])
def get_movies_by_category(category: str):
    data = list(filter(lambda movie: movie['category'] == category, movies))
    if len(data) == 0:
        return {"error": "Category not found"}
    return data


@app.get("/movies/year/", tags=["movies"])
def get_movies_by_category(year: int):
    data = list(filter(lambda movie: movie['year'] == year, movies))
    if len(data) == 0:
        return {"error": "No movies found for this year"}
    return data


@app.post('/movie', tags=["movies"])
def create_movie(movie: Movie):
    movies.append(movie.dict())
    return movies[-1]


@app.put('/movies/', tags=["movies"])
def update_movie(movie: Movie):
    for movie in movies:
        if movie['id'] == movie.id:
            movie['name'] = movie.name
            movie['year'] = movie.year
            movie['overview'] = movie.overview
            movie['rating'] = movie.rating
            movie['category'] = movie.category
            return movie

    return {"error": "Movie not found"}


@app.delete('/movies/{id}', tags=["movies"])
def update_movie(id: int):
    for movie in movies:
        if movie['id'] == id:

            movies.remove(movie)
            return {'message': 'Movie deleted', 'id': movie['id']}

    return {"error": "Movie not found"}
