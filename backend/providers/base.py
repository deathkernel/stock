from abc import ABC, abstractmethod
from dataclasses import dataclass
import pandas as pd

@dataclass
class ProviderResult:
    provider: str
    symbol: str
    data: pd.DataFrame
    metadata: dict

class MarketDataProvider(ABC):
    name: str

    @abstractmethod
    async def history(self, symbol: str, interval: str = "1day", outputsize: int = 500) -> ProviderResult:
        raise NotImplementedError
