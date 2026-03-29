"""
facade.deliverable - Deliverable content generation endpoints.

Depends: fastapi
Consumers: main (router inclusion)
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/deliverable", tags=["deliverable"])


@router.get("/")
async def list_deliverables() -> dict[str, object]:
    """List generated deliverables."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet"
    )


@router.post("/")
async def create_deliverable() -> dict[str, str]:
    """Create a new deliverable."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet"
    )
