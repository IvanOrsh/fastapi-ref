from fastapi import FastAPI

app = FastAPI()


@app.get("/hello")
def hello():
    return {
        "Hello": "How are you doing?",
    }


@app.get("/")
def root():
    return {"root": "root"}
