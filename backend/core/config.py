from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = "sqlite+aiosqlite:///./db.sqlite3"
    db_echo: bool = True


settings = Settings()

WHITELIST = [
    "http://localhost:5000/",
    "http://localhost:5001/",
    "http://localhost:5002/",
    "http://localhost:5003/",
]
