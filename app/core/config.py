from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./leadbot.db"

    notify_webhook_url: str = ""

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_to: str = ""

    resend_api_key: str = ""
    alert_email_from: str = "LeadBot <onboarding@resend.dev>"
    alert_email_to: str = ""

    crm_url: str = "https://leadbot-ai-crm.onrender.com/crm/leads"

    ai_provider: str = "rules"  # rules | openai
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    business_name: str = "Business"
    business_hours: str = "08:00–20:00"
    business_location: str = "Your address"
    base_price_ils: int = 150


settings = Settings()
