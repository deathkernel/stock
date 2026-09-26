from backend.providers.alpha_vantage import AlphaVantageProvider
from backend.providers.twelve_data import TwelveDataProvider
from backend.providers.finnhub import FinnhubProvider
from backend.providers.stooq import StooqProvider
from backend.providers.yahoo_finance import YahooFinanceProvider
from backend.data.normalize import normalize_ohlcv

class ProviderOrchestrator:
    def __init__(self):
        self.providers=[AlphaVantageProvider(),TwelveDataProvider(),FinnhubProvider(),StooqProvider(),YahooFinanceProvider()]
    async def history(self,symbol:str,outputsize:int=500):
        errors=[]
        for provider in self.providers:
            try:
                result=await provider.history(symbol,outputsize=outputsize)
                result.data=normalize_ohlcv(result.data)
                if not result.data.empty:return result,errors
            except Exception as exc: errors.append({"provider":provider.name,"error":str(exc)})
        raise RuntimeError(f"No market data provider succeeded: {errors}")
