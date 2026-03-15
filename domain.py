from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class CurrencyRate:
    """Бизнес-сущность курса валюты"""
    code: str
    value: float
    date: date

class CurrencyRepository(ABC):
    """Абстракция репозитория - порт в доменном слое"""
    
    @abstractmethod
    async def get_rate(self, currency_code: str, rate_date: Optional[date] = None) -> Optional[CurrencyRate]:
        """Получить курс валюты"""
        pass