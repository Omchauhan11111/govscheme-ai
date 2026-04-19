import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MONGO_URI: str = os.getenv("MONGO_URI", "")
    DB_NAME: str = "gov_ai_project"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    WP_URL: str = os.getenv("WP_URL", "https://govscheme.infinityfreeapp.com/wp-json")
    WP_USER: str = os.getenv("WP_USER", "admin")
    WP_PASSWORD: str = os.getenv("WP_PASSWORD", "")
    GMAIL_USER: str = os.getenv("GMAIL_USER", "")
    GMAIL_PASSWORD: str = os.getenv("GMAIL_PASSWORD", "")
    NOTIFY_EMAIL: str = os.getenv("NOTIFY_EMAIL", "")
    SCHEDULER_INTERVAL_MINUTES: int = int(os.getenv("SCHEDULER_INTERVAL", "1440"))
    RSS_FEEDS: list = [
        "https://news.google.com/rss/search?q=government+scheme+india&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=pradhan+mantri+yojana&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=india+government+subsidy+scheme+2024&hl=en-IN&gl=IN&ceid=IN:en",
    ]
    APP_NAME: str = "GovScheme AI Monitor"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

settings = Settings()