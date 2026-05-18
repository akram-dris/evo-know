from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "KM API Gateway"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_db: str = "km_knowledge_base"
    postgres_user: str = "km_admin"
    postgres_password: str = "km_secure_password_2026"
    kafka_bootstrap_servers: str = "localhost:9092"
    jwt_secret_key: str = "km_super_secret_jwt_key_2026"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
