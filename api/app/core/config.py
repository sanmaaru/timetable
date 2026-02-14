from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configs(BaseSettings):

    DEBUG: bool = True

    DATABASE_URL: str = Field(alias='CONNECTION')

    JWT_SECRET: str
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = 10

    REFRESH_TOKEN_EXPIRE_DAY = 30

    THEME_DEFAULT_COLOR = '#2B2A2A'
    THEME_DEFAULT_TEXT_COLOR = '#EEEEEE'

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True,
    )


configs = Configs()