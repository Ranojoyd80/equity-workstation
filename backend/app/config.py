from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")

    alpha_vantage_api_key: str = ""
    data_dir: Path = ROOT / "data"
    db_path: Path = ROOT / "data" / "workstation.duckdb"


settings = Settings()
