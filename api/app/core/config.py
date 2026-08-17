from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configs(BaseSettings):

    DEBUG: bool

    # Database configs
    DB_DATABASE: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f'mysql+asyncmy://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}?ssl=true'


    # Auth configs
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10

    REFRESH_TOKEN_EXPIRE_DAY: int = 30

    ID_TOKEN_LENGTH: int

    # Administrator configs
    ADMINISTRATOR_NAME: str = '관리자'
    ADMINISTRATOR_TOKEN: str
    ADMINISTRATOR_IDENTITY_ID: str

    # Semester configs
    DEFAULT_SEMESTER_CODE: str = 'DEFAULT_SEMESTER'

    # Theme configs
    THEME_DEFAULT_COLOR: str = '#2B2A2A'
    THEME_DEFAULT_TEXT_COLOR: str = '#EEEEEE'

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True,
    )


configs = Configs()