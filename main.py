from fastapi import FastAPI, Request

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

