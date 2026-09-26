from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./stock.db"
    alpha_vantage_api_key: str | None = None
    twelve_data_api_key: str | None = None
    finnhub_api_key: str | None = None
    fmp_api_key: str | None = None
    tiingo_api_key: str | None = None
    eodhd_api_key: str | None = None
    massive_api_key: str | None = None
    fred_api_key: str | None = None
    newsapi_api_key: str | None = None
    sec_user_agent: str = "Stock Intelligence research contact@example.com"
    request_timeout_seconds: int = 20
    cache_ttl_seconds: int = 900
    cache_max_entries: int = 256
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
