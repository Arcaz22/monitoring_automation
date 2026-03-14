from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    waha_base_url: str
    waha_api_key:  str
    waha_session:  str
    waha_dashboard_username:  str
    waha_dashboard_password:  str

    trello_api_key: str
    trello_token:   str
    trello_board_id: str

    scheduler_hour:   int
    scheduler_minute: int

    test_phone: str

    app_env:  str
    app_host: str
    app_port: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
