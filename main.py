from fastapi import Depends, FastAPI, Body, HTTPException, Path, Query, Request
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List

from jwt_manager import create_token, validate_token


class JWTToken(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != "josegaldamez1991@gmail.com":
            raise HTTPException(status_code=401, detail="Invalid credentials")


class User(BaseModel):
    email: str
    password: str


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


@app.post("/login", tags=["auth"])
def login(user: User) -> dict:
    if user.email == "josegaldamez1991@gmail.com" and user.password == "1234":
        token = create_token(user.dict())
        return JSONResponse(content={"token": token}, status_code=200)

    return JSONResponse(content={"error": "Invalid credentials"}, status_code=401)


@app.get("/", tags=["movies"], response_model=List[Movie], dependencies=[Depends(JWTToken())])
def get_movies() -> List[Movie]:
    return JSONResponse(content=movies, status_code=200)


@app.get("/movies/{id}", tags=["movies"], response_model=Movie)
def get_movies(id: int = Path(ge=1, le=len(movies))) -> Movie:
    for movie in movies:
        if movie['id'] == id:
            return JSONResponse(content=movie, status_code=200)
    return JSONResponse(content={"error": "Movie not found"}, status_code=404)


@app.get("/movies/category/", tags=["movies"], response_model=List[Movie])
def get_movies_by_category(category: str = Query(min_length=1, max_length=15)):
    data = list(filter(lambda movie: movie['category'] == category, movies))
    if len(data) == 0:
        return JSONResponse(content={"error": "Category not found"}, status_code=404)
    return JSONResponse(content=data, status_code=200)


@app.get("/movies/year/", tags=["movies"], response_model=List[Movie])
def get_movies_by_category(year: int):
    data = list(filter(lambda movie: movie['year'] == year, movies))
    if len(data) == 0:
        return JSONResponse(content={"error": "No movies found for this year"}, status_code=404)
    return JSONResponse(content=data, status_code=200)


@app.post('/movie', tags=["movies"], response_model=Movie)
def create_movie(movie: Movie) -> Movie:
    movies.append(movie.dict())
    return JSONResponse(content=movies[-1], status_code=201)


@app.put('/movies/', tags=["movies"], response_model=dict)
def update_movie(movie_path: Movie) -> dict:
    for movie in movies:
        if movie['id'] == movie_path.id:
            movie['name'] = movie_path.name
            movie['year'] = movie_path.year
            movie['overview'] = movie_path.overview
            movie['rating'] = movie_path.rating
            movie['category'] = movie_path.category
            return JSONResponse(content=movie_path.dict(), status_code=200)

    return JSONResponse(content={"error": "Movie not found"}, status_code=404)


@app.delete('/movies/{id}', tags=["movies"], response_model=dict)
def update_movie(id: int) -> dict:
    for movie in movies:
        if movie['id'] == id:
            movies.remove(movie)
            return JSONResponse({'message': 'Movie deleted', 'id': movie['id']}, status_code=200)

    return JSONResponse(content={"error": "Movie not found"}, status_code=404)
