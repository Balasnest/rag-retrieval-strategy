from pydantic import BaseModel
from typing import Any, Optional


class StubResponse(BaseModel):
    """Every Phase 1 endpoint returns this shape so the frontend can wire
    up real UI against a stable contract before the real logic exists.
    `implemented=False` is the signal the frontend uses to render a
    'not built yet' state instead of treating placeholder data as real."""
    implemented: bool = False
    phase_planned: str
    message: str
    data: Optional[Any] = None
