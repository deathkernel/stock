from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    app_env:str="development"
    database_url:str="sqlite:///./stock.db"
    alpha_vantage_api_key:str|None=None
    twelve_data_api_key:str|None=None
    finnhub_api_key:str|None=None
    sec_user_agent:str="Stock Intelligence research contact@example.com"
    request_timeout_seconds:int=20
    cache_ttl_seconds:int=900
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")

settings=Settings()
