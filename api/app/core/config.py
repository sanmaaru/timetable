from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configs(BaseSettings):

    DEBUG: bool

    SQL_ROOT_PASSWORD: str
    SQL_DATABASE: str
    SQL_USER: str
    SQL_PASSWORD: str
    SQL_HOST: str = 'db'
    SQL_PORT: int = 3306

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f'mariadb+aiomysql://{self.SQL_USER}:{self.SQL_PASSWORD}@{self.SQL_HOST}:{self.SQL_PORT}/{self.SQL_DATABASE}'

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10

    REFRESH_TOKEN_EXPIRE_DAY: int = 30

    THEME_DEFAULT_COLOR: str = '#2B2A2A'
    THEME_DEFAULT_TEXT_COLOR: str = '#EEEEEE'

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True,
    )


configs = Configs()