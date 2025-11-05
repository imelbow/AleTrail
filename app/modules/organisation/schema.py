import uuid

from pydantic import BaseModel, Field



class OrganisationCreatePayload(BaseModel):
    title: str = Field(min_length=2, max_length=100)


class Organisation(BaseModel):
    id: uuid.UUID | None = None
    title: str | None = None
    role: str | None = None
