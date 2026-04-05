from fastapi import APIRouter, Query
from datetime import datetime
from application import GetCurrencyRateUseCase
from infrastructure import CbrRepository
import os

# Инициализируем роутер
router = APIRouter()

# Вынес в константу переменную имени сервиса
SERVICE_NAME = "currency"

# Получаю URL, создаю репо
cbr_url = os.getenv('CBR_URL', 'http://www.cbr.ru/scripts/XML_daily.asp')
repository = CbrRepository(cbr_url)
use_case = GetCurrencyRateUseCase(repository)


# Создание ручки(эндпоинта) для получения общей информации
@router.get('/info')
async def info():
    return {
        'version': os.getenv('VERSION', '1.0.0'),
        'service': os.getenv('SERVICE', SERVICE_NAME),
        'author': os.getenv('AUTHOR', 'i.chach')
    }


# Создание ручки(эндпоинта) для получения курсов валют
@router.get('/info/currency')
async def currency_rate(
    currency: str = Query(None),
    date: str = Query(None)
):
    rate_date = None
    # Условие для формата даты
    if date:
        try:
            rate_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return {'data': {}, 'service': SERVICE_NAME}
    # Условия для получения всех валют, если валюта не указана
    if not currency:
        rates = await use_case.get_all_rates(rate_date)
        return {
            'data': {rate.code: rate.value for rate in rates},
            'service': SERVICE_NAME
        }
    # Условие для поиска конкретной валюта и чуть ниже вывод,
    # если валюта не найдена
    rate = await use_case.execute(currency, rate_date)

    if not rate:
        return {'data': {}, 'service': SERVICE_NAME}

    return {
        'data': {rate.code: rate.value},
        'service': SERVICE_NAME
    }
