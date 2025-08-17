def test_signup_and_login(client):
    # signup
    r = client.post("/signup", json={"username": "u1", "password": "p1"})
    assert r.status_code == 201

    # login (OAuth2 password form)
    r = client.post(
        "/token",
        data={"username": "u1", "password": "p1"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    token = r.json().get("access_token")
    assert token and isinstance(token, str)
