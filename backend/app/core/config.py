from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    driver: str
    user: str
    password: str
    host: str
    port: int = 5432
    db_name: str

    upload_dir: str
    placeholder_path: str

    jwt_secret_key: str
    jwt_refresh_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_days: int
    google_client_id: str
    google_client_secret: str

    @computed_field
    @property
    def absolute_upload_dir(self) -> Path:
        return BASE_DIR / self.upload_dir

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        extra='ignore'
    )


settings = Settings()