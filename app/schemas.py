from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class UserCreate(BaseModel):
    username: str = Field(
        min_length=2,
        max_length=100,
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        cleaned_username = value.strip()

        if len(cleaned_username) < 2:
            raise ValueError(
                "Korisničko ime mora imati najmanje 2 znaka."
            )

        return cleaned_username


class UserResponse(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class InteractionCreate(BaseModel):
    user_id: int = Field(gt=0)
    article_id: str
    interaction_type: Literal["view", "like", "purchase"]

    @field_validator("article_id")
    @classmethod
    def validate_article_id(cls, value: str) -> str:
        cleaned_article_id = value.strip()

        if not cleaned_article_id:
            raise ValueError(
                "ID proizvoda ne smije biti prazan."
            )

        return cleaned_article_id


class InteractionResponse(BaseModel):
    id: int
    user_id: int
    article_id: str
    interaction_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)