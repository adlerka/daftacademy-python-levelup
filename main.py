import datetime
from datetime import timedelta, date
from typing import Optional, List

from fastapi import FastAPI, Request, Response, Query, Cookie
from fastapi.responses import HTMLResponse
from hashlib import sha512, sha256

from pydantic.main import BaseModel

app = FastAPI()
app.counter = 0
app.patient_id = 0
app.patients_register = dict()
app.secret_key = 0


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
def authorize(response: Response, password: Optional[str] = None, password_hash: Optional[str] = None):
    response.status_code = 401
    try:
        if password and password_hash and password_hash == str(sha512(bytes(password, encoding="ASCII")).hexdigest()):
            response.status_code = 204
    except Exception:
        response.status_code = 401
    return AuthResponse(status_code=response.status_code)


class Patient(BaseModel):
    name: str
    surname: str


class RegistrationInfo(BaseModel):
    id: int
    name: str
    surname: str
    register_date: str
    vaccination_date: str


@app.post("/register", response_model=RegistrationInfo)
def register_patient(response: Response, patient: Patient):
    app.patient_id += 1
    how_many_days = sum(character.isalpha() for character in patient.name) \
                    + sum(character.isalpha() for character in patient.surname)
    registration_date = date.today()
    vaccination_date = registration_date + timedelta(days=how_many_days)
    response.status_code = 201
    app.patients_register[app.patient_id] = RegistrationInfo(
                                                id=app.patient_id,
                                                name=patient.name,
                                                surname=patient.surname,
                                                register_date=registration_date.strftime("%Y-%m-%d"),
                                                vaccination_date=vaccination_date.strftime("%Y-%m-%d")
                                            )
    return app.patients_register[app.patient_id]


@app.get("/patient/{id}", response_model=Optional[RegistrationInfo])
def get_patient(response: Response, id: int):
    if id < 1:
        response.status_code = 400
    elif id not in app.patients_register:
        response.status_code = 404
    else:
        response.status_code = 200
        return app.patients_register[id]


@app.get("/hello", response_class=HTMLResponse)
def hello():
    today = date.today()
    return f"""
    <html>
        <body>
            <h1>Hello! Today date is {today.strftime("%Y-%m-%d")}</h1>
        </body>
    </html>
    """


@app.post("/login_session")
def create_session(response: Response, query: List[str] = Query(None)):
    response.status_code = 401
    if query is not None and "4dm1n" and "NotSoSecurePa$$" in query:
        response.status_code = 201
        session_token = sha256(f"4dm1nNotSoSecurePa$${app.secret_key}".encode()).hexdigest()
        response.set_cookie(key="session_token", value=session_token)
        app.secret_key += 1


@app.post("/login_token")
def check_token(response: Response, query: List[str] = Query(None), session_token: str = Cookie(None)):
    response.status_code = 401
    if query is not None and "4dm1n" and "NotSoSecurePa$$" in query:
        response.status_code = 201
        return {"token": session_token}
