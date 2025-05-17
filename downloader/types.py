import typing as T

from pydantic import BaseModel


class Download(BaseModel):
    url: str
    path: T.Optional[str] = None
