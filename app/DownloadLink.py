from pydantic import BaseModel, AnyUrl


class DownloadLink(BaseModel):
    url: AnyUrl

    # Example for docs
    class Config:
        schema_extra = {
            "example": {
                "url": "https://cdn-download-path",
            }
        }
