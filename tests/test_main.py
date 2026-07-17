def test_post_shorten_valid_url_returns_short_code(client, sample_url):
    response = client.post("/shorten", json=sample_url)
    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == sample_url["original_url"]
    assert "short_code" in data
    assert "short_url" in data
    assert data["access_count"] == 0
    assert data["is_custom"] is False


def test_post_shorten_same_url_twice_returns_same_code(client, sample_url):
    resp1 = client.post("/shorten", json=sample_url)
    assert resp1.status_code == 201
    code1 = resp1.json()["short_code"]

    resp2 = client.post("/shorten", json=sample_url)
    assert resp2.status_code == 200
    assert resp2.json()["short_code"] == code1
    assert resp2.json()["access_count"] == 0


def test_post_shorten_with_custom_alias(client):
    payload = {"original_url": "https://python.org", "custom_alias": "mypython"}
    response = client.post("/shorten", json=payload)
    assert response.status_code == 201
    assert response.json()["short_code"] == "mypython"
    assert response.json()["is_custom"] is True

    redirect = client.get("/mypython", follow_redirects=False)
    assert redirect.status_code == 301
    assert redirect.headers["location"] == "https://python.org"


def test_get_code_redirects_to_original_url(client, sample_url):
    create_resp = client.post("/shorten", json=sample_url)
    short_code = create_resp.json()["short_code"]

    response = client.get(f"/{short_code}", follow_redirects=False)
    assert response.status_code == 301
    assert response.headers["location"] == sample_url["original_url"]


def test_get_code_unknown_code_returns_404(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_url_validation_rejects_invalid_urls(client):
    response = client.post("/shorten", json={"original_url": "not-a-url"})
    assert response.status_code == 422

    response = client.post("/shorten", json={"original_url": "ftp://bad.com"})
    assert response.status_code == 422


def test_custom_alias_conflict_handling(client):
    payload = {"original_url": "https://python.org", "custom_alias": "mypy"}
    client.post("/shorten", json=payload)

    payload2 = {"original_url": "https://different.org", "custom_alias": "mypy"}
    response = client.post("/shorten", json=payload2)
    assert response.status_code == 409
    data = response.json()
    assert "detail" in data
