from fastapi import Depends, FastAPI, Body, HTTPException, Path, Query, Request
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from jwt_manager import create_token, validate_token
from config.database import Base, engine, Session
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder


Base.metadata.create_all(bind=engine)


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
    title: str = Field(default="No name", max_length=100, min_length=1)
    year: int = Field(default=2020, ge=1900, le=2023)
    overview: str = Field(default="No overview", max_length=1000, min_length=5)
    rating: float = Field(default=0.0, ge=0.0, le=10.0)
    category: str = Field(default="No category", max_length=100, min_length=1)

    class Config():
        schema_extra = {
            "example": {
                "id": 5,
                "title": "The Matrix",
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

]


@app.post("/login", tags=["auth"])
def login(user: User) -> dict:
    if user.email == "josegaldamez1991@gmail.com" and user.password == "1234":
        token = create_token(user.dict())
        return JSONResponse(content={"token": token}, status_code=200)

    return JSONResponse(content={"error": "Invalid credentials"}, status_code=401)


@app.get("/", tags=["movies"], response_model=List[Movie], dependencies=[Depends(JWTToken())])
def get_movies() -> List[Movie]:
    db = Session()
    result = db.query(MovieModel).all()
    return JSONResponse(content=jsonable_encoder(result), status_code=200)


@app.get("/movies/{id}", tags=["movies"], response_model=Movie)
def get_movies(id: int = Path()) -> Movie:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == id).first()
    if not result:
        return JSONResponse(content={"error": "Movie not found"}, status_code=404)
    return JSONResponse(content=jsonable_encoder(result), status_code=200)


@app.get("/movies/category/", tags=["movies"], response_model=List[Movie])
def get_movies_by_category(category: str = Query(min_length=1, max_length=15)):
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.category == category).all()
    if not result:
        return JSONResponse(content={"error": "Category not found"}, status_code=404)
    return JSONResponse(content=jsonable_encoder(result), status_code=200)


@app.get("/movies/year/", tags=["movies"], response_model=List[Movie])
def get_movies_by_category(year: int):
    data = list(filter(lambda movie: movie['year'] == year, movies))
    if len(data) == 0:
        return JSONResponse(content={"error": "No movies found for this year"}, status_code=404)
    return JSONResponse(content=data, status_code=200)


@app.post('/movie', tags=["movies"])
def create_movie(movie: Movie):
    db = Session()
    new_movie = MovieModel(**movie.dict())
    db.add(new_movie)
    db.commit()
    return JSONResponse(content={
        "success": True,
        "message": "La película se a creado con exito"
    }, status_code=201)


@app.put('/movies/', tags=["movies"], response_model=dict)
def update_movie(id: int, movie_path: Movie) -> dict:

    db = Session()
    result = db.query(MovieModel).filter(
        MovieModel.id == id).first()
    if not result:
        return JSONResponse(content={"error": "Movie not found", "success": False}, status_code=404)

    result.title = movie_path.title
    result.year = movie_path.year
    result.overview = movie_path.overview
    result.rating = movie_path.rating
    result.category = movie_path.category
    db.commit()
    return JSONResponse(content={"message": "Se ha modificado la película", "success": True}, status_code=200)


@app.delete('/movies/{id}', tags=["movies"], response_model=dict)
def update_movie(id: int) -> dict:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == id).first()
    if not result:
        return JSONResponse(content={"error": "Movie not found", "success": False}, status_code=404)

    db.delete(result)
    db.commit()
    return JSONResponse(content={"message": "Pelicula borrada correctamnte", "success": True}, status_code=200)
