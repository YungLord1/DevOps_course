import pytest
from datetime import date
from unittest.mock import AsyncMock, patch

# Наши модули
from infrastructure import CbrRepository
from domain import CurrencyRate
from presentation import router
from fastapi.testclient import TestClient

# Создаем клиент для тестов FastAPI
client = TestClient(router)


@pytest.mark.asyncio
async def test_cbr_xml_parsing():

    repo = CbrRepository("http://www.cbr.ru/scripts/XML_daily.asp")
    mock_xml = """
    <ValCurs Date="17.01.2023" name="Foreign Currency Market">
        <Valute ID="R01235">
            <CharCode>USD</CharCode>
            <Value>68,2892</Value>
        </Valute>
    </ValCurs>
    """

    # мок httpx внутри репозитория
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.text = mock_xml
        mock_get.return_value.status_code = 200

        rate = await repo.get_rate("USD", date(2023, 1, 17))

        # проверка на то, что запятая превратилась в точку и число стало float
        assert rate.code == "USD"
        assert rate.value == 68.2892
        assert isinstance(rate.value, float)


@pytest.mark.asyncio
async def test_cbr_error_handling():
    repo = CbrRepository("http://www.cbr.ru/scripts/XML_daily.asp")

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.text = "Error in parameters"
        mock_get.return_value.status_code = 200

        rate = await repo.get_rate("USD")
        assert rate is None


# проверка, что info в нужном формате
def test_api_info():

    res = client.get("/info")
    assert res.status_code == 200
    assert res.json()["service"] == "currency"


@pytest.mark.asyncio
async def test_api_currency_success():

    mock_rate = CurrencyRate(code="USD", value=68.2892, date=date(2023, 1, 17))
    with patch("application.GetCurrencyRateUseCase.execute",
               new_callable=AsyncMock) as mock_exe:
        mock_exe.return_value = mock_rate

        res = client.get("/info/currency?currency=USD&date=2023-01-17")

        assert res.status_code == 200
        res = res.json()

        # целевой формат
        assert res["data"]["USD"] == 68.2892
        assert res["service"] == "currency"
