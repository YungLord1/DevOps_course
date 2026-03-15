from datetime import date
from typing import Optional
from domain import CurrencyRate, CurrencyRepository

class GetCurrencyRateUseCase:
    def __init__(self, repository: CurrencyRepository):
        self.repository = repository
    
    async def execute(self, currency_code: str, rate_date: Optional[date] = None) -> Optional[CurrencyRate]:
        if not currency_code or len(currency_code) != 3:
            return None
        
        try:
            return await self.repository.get_rate(currency_code.upper(), rate_date)
        except:
            return None