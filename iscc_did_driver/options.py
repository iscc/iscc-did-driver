from pydantic import BaseSettings, Field, HttpUrl


class Options(BaseSettings):
    class Config:
        env_file = ".env"
        env_prefix = "ISCC_DID_DRIVER_"
        env_file_encoding = "utf-8"

    debug: bool = Field(False, description="Run application in debug mode (default: False)")
    iscc_registry: HttpUrl = Field(
        "https://iscc.id", description="URL to an ISCC registry instantiation."
    )


opts = Options()
