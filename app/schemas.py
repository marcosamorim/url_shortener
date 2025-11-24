from pydantic import BaseModel, AnyHttpUrl


class ShortenRequest(BaseModel):
    url: AnyHttpUrl


class ShortenResponse(BaseModel):
    code: str
    short_url: str
    original_url: str

# TODO: add metadata too
class ShortUrlStats(BaseModel):
    code: str
    original_url: str
    clicks: int
