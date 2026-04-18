from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Optional, List


# Доменная модель для представления курса валют, бизнес-логика
@dataclass
class CurrencyRate:
    code: str
    value: float
    date: date

    # Интерфейс(абстрактный класс) для репо курсов валют


class CurrencyRepository(ABC):

    # Получение курса конкретной валюты
    @abstractmethod
    async def get_rate(
        self, currency_code: str, rate_date: Optional[date] = None
    ) -> Optional[CurrencyRate]:
        pass

    # Получение курса всех валют
    @abstractmethod
    async def get_all_rates(self, rate_date: Optional[date] = None
                            ) -> List[CurrencyRate]:
        pass
