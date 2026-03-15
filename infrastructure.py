import httpx
import xml.etree.ElementTree as ET
from datetime import date
from typing import Optional
from domain import CurrencyRate, CurrencyRepository

class CbrRepository(CurrencyRepository):
    """Реализация порта - адаптер инфраструктуры"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def get_rate(self, currency_code: str, rate_date: Optional[date] = None) -> Optional[CurrencyRate]:
        """Реализация метода из абстрактного класса CurrencyRepository"""

        url = self.base_url
        if rate_date:
            date_str = rate_date.strftime("%d/%m/%Y")
            url = f"{self.base_url}?date_req={date_str}"
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                
                if "Error in parameters" in resp.text:
                    raise ValueError("Некорректная дата для ЦБ РФ")
                
                root = ET.fromstring(resp.text)
                
                for valute in root.findall('Valute'):
                    if valute.find('CharCode').text == currency_code:
                        value_str = valute.find('Value').text.replace(',', '.')
                        value = float(value_str)
                        
                        return CurrencyRate(
                            code=currency_code,
                            value=value,
                            date=rate_date or date.today()
                        )
                
                return None
                
            except httpx.HTTPError as e:
                raise ConnectionError(f"Ошибка подключения к ЦБ РФ: {e}")
            except ET.ParseError:
                raise ValueError("Ошибка парсинга ответа от ЦБ РФ")