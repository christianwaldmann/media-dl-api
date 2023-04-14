from pydantic import BaseModel, AnyUrl


class Video(BaseModel):
    url: AnyUrl

    # Example for docs
    class Config:
        schema_extra = {
            "example": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            }
        }
