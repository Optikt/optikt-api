from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AccessTokenData(BaseModel):
    """
    Pydantic model for the expected structure of the JWT claims.
    It performs validation when created from the decoded dictionary.
    """

    # Subject (User ID - UUID format) - required
    sub: UUID
    # Expiration timestamp - optional for definition, but usually present
    exp: Optional[datetime] = None
