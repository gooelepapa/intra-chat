from pydantic import BaseModel, HttpUrl


class NewsArticle(BaseModel):
    title: str
    url: HttpUrl
    source: str
    content: str
