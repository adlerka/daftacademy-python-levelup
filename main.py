from fastapi import FastAPI, Request, Response
from hashlib import sha512

from pydantic.main import BaseModel

app = FastAPI()
app.counter = 0


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/hello/{name}")
def hello_name_view(name: str):
    return f"Hello {name}"


@app.get("/counter")
def counter():
    app.counter += 1
    return str(app.counter)


@app.get("/method", status_code=200)
@app.put("/method", status_code=200)
@app.options("/method", status_code=200)
@app.delete("/method", status_code=200)
@app.post("/method", status_code=201)
def read_method(request: Request):
    return {"method": request.method}


class AuthResponse(BaseModel):
    status_code: int


@app.get("/auth", response_model=AuthResponse)
def authorize(password: str, password_hash: str, response: Response):
    response.status_code = 401
    try:
        if password and password_hash and password_hash == str(sha512(bytes(password, encoding="ASCII")).hexdigest()):
            response.status_code = 204
    except Exception:
        response.status_code = 401
    return AuthResponse(status_code=response.status_code)

