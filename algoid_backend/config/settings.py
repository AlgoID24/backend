from datetime import timedelta
from pydantic.fields import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(default="")
    echo_sql: bool = Field(default=True)
    secret_key: str = Field(default="")
    allowed_hosts: str = Field(default="")
    auth_token_token_valid_duration: timedelta = Field(default=timedelta(minutes=10))
    auth_token_refresh_token_valid_duration: timedelta = Field(
        default=timedelta(days=1)
    )

    class Config:
        env_file = ".env"


settings = Settings()
