"""
facade.deliverable - Deliverable content generation endpoints.

Depends: fastapi
Consumers: main (router inclusion)
"""

from fastapi import APIRouter

router = APIRouter(prefix="/deliverable", tags=["deliverable"])


@router.get("/")
async def list_deliverables() -> dict[str, object]:
    """List generated deliverables."""
    return {"deliverables": [], "total": 0}


@router.post("/")
async def create_deliverable() -> dict[str, str]:
    """Create a new deliverable."""
    return {"message": "Not implemented yet"}
