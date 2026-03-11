"""
facade.roundtable - Roundtable discussion session endpoints.

Depends: fastapi
Consumers: main (router inclusion)
"""

from fastapi import APIRouter

router = APIRouter(prefix="/roundtable", tags=["roundtable"])


@router.get("/sessions")
async def list_sessions() -> dict[str, object]:
    """List discussion sessions."""
    return {"sessions": [], "total": 0}


@router.post("/sessions")
async def create_session() -> dict[str, str]:
    """Create a new discussion session."""
    return {"message": "Not implemented yet"}
