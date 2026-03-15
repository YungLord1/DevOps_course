from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Optional, List

@dataclass
class CurrencyRate:
    code: str
    value: float
    date: date

class CurrencyRepository(ABC):
    @abstractmethod
    async def get_rate(self, currency_code: str, rate_date: Optional[date] = None) -> Optional[CurrencyRate]:
        pass
    
    @abstractmethod
    async def get_all_rates(self, rate_date: Optional[date] = None) -> List[CurrencyRate]:
        pass