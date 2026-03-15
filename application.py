from datetime import date
from typing import Optional
from domain import CurrencyRate, CurrencyRepository

class GetCurrencyRateUseCase:
    """Сценарий использования - зависит только от абстракции (порта)"""
    
    def __init__(self, repository: CurrencyRepository):
        self._repository = repository
    
    async def execute(self, currency_code: str, rate_date: Optional[date] = None) -> Optional[CurrencyRate]:
        """Бизнес-логика получения курса"""
        
        if not currency_code:
            raise ValueError("Код валюты не может быть пустым")
        
        if len(currency_code) != 3:
            raise ValueError("Код валюты должен состоять из 3 символов")
        
        if not currency_code.isalpha():
            raise ValueError("Код валюты должен содержать только буквы")
        
        if rate_date and rate_date > date.today():
            raise ValueError("Нельзя получить курс на будущую дату")
        
        return await self._repository.get_rate(currency_code.upper(), rate_date)