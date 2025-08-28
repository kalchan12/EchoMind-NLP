from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str | None = None
    elevenlabs_api_key: str | None = None
    whisper_model_size: str = "small"
    stt_language: str = "en"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


