TORTOISE_ORM = {
    "connections": {"default": "sqlite:///backend/src/database/users.db"},
    "apps": {
        "models": {
            "models": [
                "backend.src.database.models",
                "aerich.models"
            ],
            "default_connection": "default"
        }
    }
}
