TORTOISE_ORM = {
    "connections": {"default": "postgres://postgres:postgres@localhost:5432/blockchain"},
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
