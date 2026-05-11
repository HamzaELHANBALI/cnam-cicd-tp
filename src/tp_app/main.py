"""FastAPI application exposing calculator and text tools."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from tp_app.calculator import add, divide, multiply, subtract
from tp_app.text_tools import count_words, reverse, slugify
import logging

app = FastAPI(
    title="CNAM CI/CD Demo API",
    description="A simple API to showcase CI/CD with GitHub Actions and Render.",
    version="1.0.0",
)


class CalcRequest(BaseModel):
    left: float
    right: float


class TextRequest(BaseModel):
    text: str


@app.get("/")
def root():
    return {"status": "ok", "message": "CNAM CI/CD Demo API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/calc/add")
def calc_add(body: CalcRequest):
    return {"result": add(body.left, body.right)}


@app.post("/calc/subtract")
def calc_subtract(body: CalcRequest):
    return {"result": subtract(body.left, body.right)}


@app.post("/calc/multiply")
def calc_multiply(body: CalcRequest):
    return {"result": multiply(body.left, body.right)}


@app.post("/calc/divide")
def calc_divide(body: CalcRequest):
    try:
        return {"result": divide(body.left, body.right)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/text/reverse")
def text_reverse(body: TextRequest):
    return {"result": reverse(body.text)}


@app.post("/text/count-words")
def text_count_words(body: TextRequest):
    return {"result": count_words(body.text)}


@app.post("/text/slugify")
def text_slugify(body: TextRequest):
    return {"result": slugify(body.text)}
