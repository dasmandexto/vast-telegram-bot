import logging
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token: str
    vast_api_key: str
    admin_ids: List[int]
    vast_api_base_url: str = "https://console.vast.ai"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: Union[str, int, List[Union[str, int]]]) -> List[int]:
        if isinstance(v, (int, str)) and not isinstance(v, str) or (isinstance(v, str) and v.isdigit()):
            return [int(v)]
        if isinstance(v, str):
            cleaned = [item.strip() for item in v.split(",") if item.strip()]
            return [int(x) for x in cleaned if x.isdigit() or (x.startswith("-") and x[1:].isdigit())]
        if isinstance(v, list):
            return [int(x) for x in v]
        raise ValueError("Invalid format for ADMIN_IDS. Expected comma-separated IDs or list of ints.")

    @property
    def logging_level(self) -> int:
        return getattr(logging, self.log_level.upper(), logging.INFO)


def load_settings() -> Settings:
    return Settings()
