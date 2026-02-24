from fastapi import APIRouter, Depends, Query, Request

from app.loader import ModelStore
from app.schemas import TrackResponse

router = APIRouter()


def get_store(request: Request) -> ModelStore:
    return request.app.state.store


@router.get("/search", response_model=list[TrackResponse])
def search_tracks(
    q: str = Query(..., min_length=1, description="Artist or track name"),
    limit: int = Query(default=20, ge=1, le=50),
    store: ModelStore = Depends(get_store),
) -> list[TrackResponse]:
    """
    Case-insensitive substring search across track names and artist names.
    Returns up to `limit` results, sorted so name-matches come before artist-only matches.
    """
    q_lower = q.strip().lower()
    meta = store.track_meta.reset_index()  # track_id becomes a column

    name_mask   = meta["name"].str.lower().str.contains(q_lower, regex=False, na=False)
    artist_mask = meta["artist"].str.lower().str.contains(q_lower, regex=False, na=False)

    # Name hits first, then artist-only hits
    hits = meta[name_mask | artist_mask].copy()
    hits["_rank"] = (~name_mask[name_mask | artist_mask]).astype(int)
    hits = hits.sort_values("_rank").head(limit)

    return [
        TrackResponse(
            track_id=row["track_id"],
            name=row["name"],
            artist=row["artist"],
            genre=row["genre"] if row["genre"] else None,
            year=int(row["year"]) if str(row["year"]) not in ("nan", "None", "") else None,
        )
        for _, row in hits.iterrows()
    ]
