from datetime import date
from typing import Optional, List
from domain import CurrencyRate, CurrencyRepository

#use_case(сценарий использования), работающий через абстраткный репозиторий(Бизнес-логика, класс не знает откуда данные)
class GetCurrencyRateUseCase:
    def __init__(self, repository: CurrencyRepository):
        
        #Внедрение зависимости
        self.repository = repository
    
    #Бизнес-логика получения валюты
    async def execute(self, currency_code: str, rate_date: Optional[date] = None) -> Optional[CurrencyRate]:
        
        #Проверка, что код валюты из 3 символов
        if not currency_code or len(currency_code) != 3:
            return None
        
        #Приведение кода валют к капсу
        try:
            return await self.repository.get_rate(currency_code.upper(), rate_date)
        except:
            return None
    
    #Аналогично с получением всех валют, только без проверок
    async def get_all_rates(self, rate_date: Optional[date] = None) -> List[CurrencyRate]:
        try:
            return await self.repository.get_all_rates(rate_date)
        except:
            return []