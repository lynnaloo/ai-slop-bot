from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    rubric_path: str = "rubric.yaml"

    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    slack_auto_scan_channels: str = ""  # comma-separated channel IDs
    auto_scan_threshold: int = 70

    cors_origins: str = "http://localhost:5173,https://ai-slop-detector.web.app,https://ehc-c-buskey-506b97.web.app"
    port: int = 8080

    @property
    def auto_scan_channel_list(self) -> list[str]:
        return [c.strip() for c in self.slack_auto_scan_channels.split(",") if c.strip()]

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()  # type: ignore[call-arg]
