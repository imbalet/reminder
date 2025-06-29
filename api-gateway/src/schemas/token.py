from pydantic import BaseModel, UUID4


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class AccesTokenData(BaseModel):
    user_id: UUID4


class RefreshTokenData(BaseModel):
    user_id: UUID4
    jti: UUID4
