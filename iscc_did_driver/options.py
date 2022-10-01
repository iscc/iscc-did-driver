from pydantic import BaseSettings, Field


class Options(BaseSettings):
    class Config:
        env_file = ".env"
        env_prefix = "ISCC_DID_DRIVER_"
        env_file_encoding = "utf-8"

    debug: bool = Field(False, description="Run application in debug mode (default: False)")


opts = Options()
