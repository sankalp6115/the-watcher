from pydantic import BaseModel

class IngestRequest(BaseModel):
    path: str

class TextRequest(BaseModel):
    text: str

class ImageRequest(BaseModel):
    path: str