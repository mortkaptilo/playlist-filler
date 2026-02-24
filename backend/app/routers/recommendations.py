from fastapi import APIRouter, Depends, Request

from app.loader import ModelStore
from app.recommender import recommend
from app.schemas import RecommendRequest, RecommendResponse

router = APIRouter()


def get_store(request: Request) -> ModelStore:
    return request.app.state.store


@router.post("/recommendations", response_model=RecommendResponse)
def get_recommendations(
    body: RecommendRequest,
    store: ModelStore = Depends(get_store),
) -> RecommendResponse:
    """
    Given a list of seed track IDs, return recommended tracks using an
    ensemble of item-based cosine similarity, user-based cosine similarity,
    and SVD matrix factorisation.
    """
    results = recommend(store, body.track_ids, top_n=body.top_n)
    return RecommendResponse(
        recommendations=results,
        seed_count=len(body.track_ids),
    )
