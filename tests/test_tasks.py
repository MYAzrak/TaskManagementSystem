API = {"X-API-Key": "123456"}


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}", **API}


def make_user_and_token(client, username="bob", password="pw"):
    client.post("/signup", json={"username": username, "password": password})
    r = client.post(
        "/token",
        data={"username": username, "password": password},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    return r.json()["access_token"]


def test_task_crud_flow(client):
    token = make_user_and_token(client)

    # create
    r = client.post(
        "/tasks", json={"title": "t1", "description": "d"}, headers=auth_headers(token)
    )
    assert r.status_code == 201
    task = r.json()
    tid = task["id"]
    assert task["status"] == "pending"

    # list
    r = client.get("/tasks", headers=auth_headers(token))
    assert r.status_code == 200
    ids = [t["id"] for t in r.json()]
    assert tid in ids

    # get one
    r = client.get(f"/tasks/{tid}", headers=auth_headers(token))
    assert r.status_code == 200
    assert r.json()["id"] == tid

    # update status
    r = client.put(
        f"/tasks/{tid}", json={"status": "completed"}, headers=auth_headers(token)
    )
    assert r.status_code == 200
    assert r.json()["status"] == "completed"

    # delete
    r = client.delete(f"/tasks/{tid}", headers=auth_headers(token))
    assert r.status_code == 204


def test_requires_api_key_and_token(client):
    token = make_user_and_token(client, "eve", "pw")

    # Missing API key -> FastAPI will 422 for missing required header
    r = client.get("/tasks", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code in (401, 422)

    # Missing token -> 401
    r = client.get("/tasks", headers={"X-API-Key": "123456"})
    assert r.status_code == 401
