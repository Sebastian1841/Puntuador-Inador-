from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator
from .avatars import normalize_avatar

Color = Annotated[str, StringConstraints(pattern=r'^#[0-9a-fA-F]{6}$')]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)]
Status = Literal['Pendiente', 'Viendo', 'Terminada']


class InputModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class ProfileInput(InputModel):
    name: Name
    color: Color = '#FF6600'
    description: str = Field(default='', max_length=120)
    avatar: str = Field(default='', max_length=2_800_000)

    @field_validator('avatar')
    @classmethod
    def validate_avatar(cls, value):
        return normalize_avatar(value)


class SeriesInput(InputModel):
    catalog_source: Literal['tvmaze', 'jikan'] = 'tvmaze'
    favorite: bool = Field(default=False, strict=True)
    title: str = Field(min_length=1, max_length=100)
    genre: Name
    year: int = Field(strict=True, ge=1900, le=2100)
    status: Status
    description: str = Field(default='', max_length=2000)
    color: Color = '#102372'
    catalog_id: int | None = Field(default=None, strict=True, gt=0)
    image_url: str = Field(default='', pattern=r'^(https://(?:static\.tvmaze\.com/uploads/images|cdn\.myanimelist\.net/images)/[a-zA-Z0-9_./-]+)?$')
    source_url: str = Field(default='', pattern=r'^(https://(?:www\.tvmaze\.com/shows/\d+/[a-zA-Z0-9-]+|myanimelist\.net/anime/\d+(?:/[a-zA-Z0-9_-]+)?))?$')
    original_title: str = Field(default='', max_length=200)


class ReviewInput(InputModel):
    series_id: int = Field(strict=True, gt=0)
    profile_id: int = Field(strict=True, gt=0)
    score: float = Field(strict=True, ge=0.5, le=5, multiple_of=0.5, allow_inf_nan=False)
    comment: str = Field(default='', max_length=2000)


class StatusInput(InputModel):
    id: int = Field(strict=True, gt=0)
    status: Status


class SettingsInput(InputModel):
    name: str = Field(min_length=1, max_length=60)
    accent: Color
    compact: bool = Field(strict=True)


class EpisodeInput(InputModel):
    season: int = Field(strict=True, ge=1, le=1000)
    number: int = Field(strict=True, ge=1, le=10000)
    title: str = Field(min_length=1, max_length=200)


class EpisodeReviewInput(InputModel):
    episode_id: int = Field(strict=True, gt=0)
    score: float = Field(strict=True, ge=0.5, le=5, multiple_of=0.5, allow_inf_nan=False)
    comment: str = Field(default='', max_length=2000)


class FavoriteInput(InputModel):
    id: int = Field(strict=True, gt=0)
    favorite: bool = Field(strict=True)


class NotesInput(InputModel):
    notes: str = Field(max_length=4000)
