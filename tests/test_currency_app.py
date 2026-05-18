import requests

base_url = "https://localhost:8001/info/currency"


def test_info():
    info_url = "https://localhost:8001/info"
    res = requests.get(info_url)
    answer = res.json()

    assert res.status_code == 200
    assert answer["service"] == "currency"


def test_usd_2022():
    params = {"currency": "USD", "date": "2022-01-17"}
    res = requests.get(base_url, params=params)
    answer = res.json()

    assert res.status_code == 200
    assert answer["data"]["USD"] == 75.7668


def test_eur_2014():
    params = {"currency": "EUR", "date": "2014-01-17"}
    res = requests.get(base_url, params=params)
    answer = res.json()

    assert res.status_code == 200
    assert answer["data"]["EUR"] == 45.4926


def test_all():
    params = {"date": "2023-03-30"}
    res = requests.get(base_url, params=params)
    answer = res.json()

    assert len(answer["data"]) > 40
