from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, FieldSerializationInfo, field_serializer


class AccessTokenData(BaseModel):
    """
    Pydantic model for the expected structure of the JWT claims.
    It performs validation when created from the decoded dictionary.
    """

    # Subject (User ID - UUID format) - required
    sub: UUID
    # Expiration timestamp - optional for definition, but usually present
    exp: Optional[datetime] = None

    # mode="plain" means runs for python & json mode, but you can specify mode="json"
    @field_serializer("sub", mode="plain")
    @classmethod
    def _serialize_sub_uuid(cls, v: UUID, info: FieldSerializationInfo) -> str:
        return str(v)
