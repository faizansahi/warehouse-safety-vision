import json
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .domain import Zone, ZoneKind


class Settings(BaseSettings):
    database_url: str = "sqlite:///./safety.db"
    yolo_weights: str = "yolo11n.pt"
    confidence_threshold: float = Field(default=0.4, gt=0, le=1)
    proximity_pixels: float = Field(default=120, gt=0)
    zones_file: str = "config/zones.example.json"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class ZoneConfig(BaseModel):
    name: str = Field(min_length=1)
    kind: ZoneKind
    polygon: list[tuple[int, int]] = Field(min_length=3)


settings = Settings()


def load_zones(path: str) -> list[Zone]:
    values = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Zone(**ZoneConfig.model_validate(item).model_dump()) for item in values["zones"]]
