from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    image_embedding_weight: float = 0.99
    text_embedding_weight: float = 0.01
    clustering_distance_threshold: float = 0.42
    clustering_distance_metric: str = 'cosine'

settings = Settings()