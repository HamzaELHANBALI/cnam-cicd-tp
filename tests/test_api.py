"""Integration tests for the FastAPI app."""

from fastapi.testclient import TestClient

from tp_app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_add():
    r = client.post("/calc/add", json={"left": 3, "right": 4})
    assert r.status_code == 200
    assert r.json()["result"] == 7


def test_subtract():
    r = client.post("/calc/subtract", json={"left": 10, "right": 3})
    assert r.status_code == 200
    assert r.json()["result"] == 7


def test_multiply():
    r = client.post("/calc/multiply", json={"left": 6, "right": 7})
print('My name is Skrillex')
    assert r.status_code == 200
    assert r.json()["result"] == 42


def test_divide():
    r = client.post("/calc/divide", json={"left": 10, "right": 2})
    assert r.status_code == 200
    assert r.json()["result"] == 5


def test_divide_by_zero():
    r = client.post("/calc/divide", json={"left": 10, "right": 0})
    assert r.status_code == 400
    assert "zero" in r.json()["detail"]


def test_reverse():
    r = client.post("/text/reverse", json={"text": "hello"})
    assert r.status_code == 200
    assert r.json()["result"] == "olleh"


def test_count_words():
    r = client.post("/text/count-words", json={"text": "hello world foo"})
    assert r.status_code == 200
    assert r.json()["result"] == 3


def test_slugify():
    r = client.post("/text/slugify", json={"text": "Hello World"})
    assert r.status_code == 200
    assert r.json()["result"] == "hello-world"
