from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional
import os


class GlobalSettings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLLBACK: bool = False


class DevConfig(GlobalSettings):
    DATABASE_URL: str = "sqlite:///data.db"
    model_config = SettingsConfigDict(env_prefix="DEV_", env_file=".env", extra="ignore")


class ProdConfig(GlobalSettings):
    model_config = SettingsConfigDict(env_prefix="PROD_", env_file=".env", extra="ignore")


class TestConfig(GlobalSettings):
    DATABASE_URL: str = "sqlite:///test.db"
    DB_FORCE_ROLLBACK: bool = True

    model_config = SettingsConfigDict(env_prefix="TEST_", extra="ignore")


@lru_cache()
def get_config(env_state: str):
    configs = {
        "dev": DevConfig,
        "prod": ProdConfig,
        "test": TestConfig
    }
    return configs[env_state]()


env_state = os.getenv("ENV_STATE", "dev")
config = get_config(env_state)