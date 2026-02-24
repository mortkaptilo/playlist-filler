from pydantic import BaseModel, Field


class TrackResponse(BaseModel):
    track_id: str
    name: str
    artist: str
    genre: str | None = None
    year: int | None = None


class RecommendRequest(BaseModel):
    track_ids: list[str] = Field(..., min_length=1, max_length=50)
    top_n: int = Field(default=20, ge=1, le=100)


class RecommendResponse(BaseModel):
    recommendations: list[TrackResponse]
    seed_count: int
