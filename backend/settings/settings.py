from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    image_embedding_weight: float = 0.55
    text_embedding_weight: float = 0.45
    clustering_distance_threshold: float = 0.42
    clustering_distance_metric: str = 'cosine'
    ingestion_batch_size: int = 32

settings = Settings()