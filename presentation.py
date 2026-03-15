from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from application import GetCurrencyRateUseCase
from infrastructure import CbrRepository
import os

router = APIRouter()

cbr_url = os.getenv('CBR_URL', 'http://www.cbr.ru/scripts/XML_daily.asp')

repository = CbrRepository(cbr_url)

use_case = GetCurrencyRateUseCase(repository)

@router.get('/info')
async def info():
    """Информация о сервисе"""
    return {
        'version': os.getenv('VERSION', '1.0.0'),
        'service': os.getenv('SERVICE', 'currency'),
        'author': os.getenv('AUTHOR', 'i.chach')
    }

@router.get('/info/currency')
async def currency_rate(
    currency: str = Query(None, description="Код валюты (USD, EUR, GBP)"),
    date: str = Query(None, description="Дата в формате YYYY-MM-DD")
):
    """Получить курс валюты на указанную дату"""
    
    rate_date = None
    if date:
        try:
            rate_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Неверный формат даты. Используйте YYYY-MM-DD"
            )
    
    try:
        rate = await use_case.execute(currency, rate_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
    
    if not rate:
        raise HTTPException(
            status_code=404,
            detail=f"Валюта {currency} не найдена"
        )
    
    return {
        'data': {rate.code: rate.value},
        'service': 'currency'
    }